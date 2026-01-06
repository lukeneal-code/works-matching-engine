import csv
import io
import uuid
from typing import List, Dict, AsyncGenerator, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UsageRecord, ProcessingBatch
from app.services.embedding import EmbeddingService
from app.services.matching import MatchingService

EXPECTED_COLUMNS = ["recording_title", "recording_artist", "work_title", "songwriter"]
COLUMN_ALIASES = {
    "recording_title": ["recording title", "track title", "track", "song title", "song"],
    "recording_artist": ["recording artist", "artist", "performer", "singer"],
    "work_title": ["work title", "composition", "composition title", "title"],
    "songwriter": ["songwriter", "writer", "composer", "author", "writers", "songwriters"]
}


class FileProcessorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()

    @staticmethod
    def detect_delimiter(content: str) -> str:
        """Detect the delimiter used in the file."""
        first_line = content.split('\n')[0] if '\n' in content else content

        # Count potential delimiters
        pipe_count = first_line.count('|')
        comma_count = first_line.count(',')
        tab_count = first_line.count('\t')

        if pipe_count >= comma_count and pipe_count >= tab_count:
            return '|'
        elif tab_count >= comma_count:
            return '\t'
        return ','

    @staticmethod
    def normalize_column_name(name: str) -> Optional[str]:
        """Map column name to standard column name."""
        name_lower = name.lower().strip()

        for standard_name, aliases in COLUMN_ALIASES.items():
            if name_lower == standard_name or name_lower in aliases:
                return standard_name

        return None

    def parse_file(self, content: str, filename: str) -> List[Dict]:
        """Parse file content into list of records."""
        delimiter = self.detect_delimiter(content)

        # Handle potential BOM
        if content.startswith('\ufeff'):
            content = content[1:]

        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

        # Map columns
        column_mapping = {}
        if reader.fieldnames:
            for col in reader.fieldnames:
                normalized = self.normalize_column_name(col)
                if normalized:
                    column_mapping[col] = normalized

        records = []
        for row_num, row in enumerate(reader, start=1):
            record = {
                "row_number": row_num,
                "original_data": dict(row)
            }

            for original_col, standard_col in column_mapping.items():
                value = row.get(original_col, "").strip()
                record[standard_col] = value if value else None

            # Only include records that have at least a title
            if record.get("work_title") or record.get("recording_title"):
                records.append(record)

        return records

    async def create_batch(self, filename: str, total_records: int) -> ProcessingBatch:
        """Create a new processing batch."""
        batch = ProcessingBatch(
            id=uuid.uuid4(),
            filename=filename,
            total_records=total_records,
            status="pending"
        )
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def create_usage_records(
        self,
        batch_id: uuid.UUID,
        records: List[Dict]
    ) -> List[UsageRecord]:
        """Create usage records from parsed data."""
        usage_records = []

        for record in records:
            usage_record = UsageRecord(
                batch_id=batch_id,
                recording_title=record.get("recording_title"),
                recording_artist=record.get("recording_artist"),
                work_title=record.get("work_title"),
                songwriter=record.get("songwriter"),
                original_row_data=record.get("original_data"),
                row_number=record.get("row_number")
            )
            self.db.add(usage_record)
            usage_records.append(usage_record)

        await self.db.commit()

        # Refresh to get IDs
        for record in usage_records:
            await self.db.refresh(record)

        return usage_records

    async def generate_embeddings(
        self,
        usage_records: List[UsageRecord],
        progress_callback=None
    ) -> None:
        """Generate embeddings for usage records."""
        for i, record in enumerate(usage_records):
            title = record.work_title or record.recording_title
            if title:
                combined_text = self.embedding_service.normalize_for_embedding(
                    title,
                    record.songwriter or ""
                )
                embedding = await self.embedding_service.get_embedding(combined_text)
                if embedding:
                    record.title_embedding = embedding

                if progress_callback:
                    await progress_callback("embedding", i + 1, len(usage_records))

        await self.db.commit()

    async def process_file(
        self,
        content: str,
        filename: str
    ) -> AsyncGenerator[Dict, None]:
        """Process an uploaded file and yield progress updates."""

        # Parse file
        yield {"stage": "parsing", "message": "Parsing file..."}
        records = self.parse_file(content, filename)

        if not records:
            yield {
                "stage": "error",
                "message": "No valid records found in file"
            }
            return

        # Create batch
        batch = await self.create_batch(filename, len(records))
        batch.status = "processing"
        batch.started_at = datetime.utcnow()
        await self.db.commit()

        yield {
            "stage": "parsed",
            "batch_id": str(batch.id),
            "total_records": len(records),
            "message": f"Found {len(records)} records"
        }

        try:
            # Create usage records
            yield {"stage": "creating_records", "message": "Creating usage records..."}
            usage_records = await self.create_usage_records(batch.id, records)

            # Generate embeddings
            yield {"stage": "generating_embeddings", "message": "Generating embeddings..."}

            async def embedding_progress(stage, current, total):
                pass  # Handled by matching progress

            await self.generate_embeddings(usage_records, embedding_progress)

            yield {
                "stage": "embeddings_complete",
                "message": "Embeddings generated"
            }

            # Run matching
            yield {"stage": "matching", "message": "Running matching algorithm..."}
            matching_service = MatchingService(self.db)

            async def match_progress(current, results):
                yield_data = {
                    "stage": "matching_progress",
                    "processed": current,
                    "total": len(usage_records),
                    "matched": results["matched"],
                    "unmatched": results["unmatched"],
                    "flagged": results["flagged"],
                    "percentage": round((current / len(usage_records)) * 100, 1)
                }
                # This callback can't yield, so we update batch instead
                batch.processed_records = current
                batch.matched_records = results["matched"]
                batch.unmatched_records = results["unmatched"]
                batch.flagged_records = results["flagged"]

            # Process in smaller batches for progress updates
            batch_size = 10
            total_results = {"matched": 0, "unmatched": 0, "flagged": 0}

            for i in range(0, len(usage_records), batch_size):
                sub_batch = usage_records[i:i + batch_size]
                results = await matching_service.process_batch(sub_batch)

                total_results["matched"] += results["matched"]
                total_results["unmatched"] += results["unmatched"]
                total_results["flagged"] += results["flagged"]

                processed = min(i + batch_size, len(usage_records))
                batch.processed_records = processed
                batch.matched_records = total_results["matched"]
                batch.unmatched_records = total_results["unmatched"]
                batch.flagged_records = total_results["flagged"]
                await self.db.commit()

                yield {
                    "stage": "matching_progress",
                    "processed": processed,
                    "total": len(usage_records),
                    "matched": total_results["matched"],
                    "unmatched": total_results["unmatched"],
                    "flagged": total_results["flagged"],
                    "percentage": round((processed / len(usage_records)) * 100, 1)
                }

            # Complete
            batch.status = "completed"
            batch.completed_at = datetime.utcnow()
            await self.db.commit()

            yield {
                "stage": "complete",
                "batch_id": str(batch.id),
                "total_records": len(usage_records),
                "matched": total_results["matched"],
                "unmatched": total_results["unmatched"],
                "flagged": total_results["flagged"],
                "message": "Processing complete"
            }

        except Exception as e:
            batch.status = "failed"
            batch.error_message = str(e)
            await self.db.commit()

            yield {
                "stage": "error",
                "batch_id": str(batch.id),
                "message": f"Processing failed: {str(e)}"
            }
