import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from rapidfuzz import fuzz
from app.models import Work, UsageRecord, MatchResult
from app.services.embedding import EmbeddingService
from app.services.ollama import OllamaService
from app.core.config import get_settings

settings = get_settings()


class MatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.ollama_service = OllamaService()

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching - lowercase, remove punctuation, collapse whitespace."""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation except spaces
        text = re.sub(r'[^\w\s]', '', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def calculate_title_similarity(title1: str, title2: str) -> float:
        """Calculate similarity between two titles using multiple methods."""
        if not title1 or not title2:
            return 0.0

        norm1 = MatchingService.normalize_text(title1)
        norm2 = MatchingService.normalize_text(title2)

        if norm1 == norm2:
            return 1.0

        # Use multiple fuzzy matching algorithms and take the best
        ratio = fuzz.ratio(norm1, norm2) / 100
        partial = fuzz.partial_ratio(norm1, norm2) / 100
        token_sort = fuzz.token_sort_ratio(norm1, norm2) / 100
        token_set = fuzz.token_set_ratio(norm1, norm2) / 100

        # Weighted average favoring token-based matches
        return max(ratio, partial * 0.95, token_sort, token_set)

    @staticmethod
    def calculate_songwriter_similarity(songwriter1: str, songwriters2: List[str]) -> float:
        """Calculate similarity between songwriter strings."""
        if not songwriter1 or not songwriters2:
            return 0.0

        norm1 = MatchingService.normalize_text(songwriter1)

        best_score = 0.0
        for sw in songwriters2:
            norm2 = MatchingService.normalize_text(sw)

            if norm1 == norm2:
                return 1.0

            # Check if one contains the other (partial match)
            if norm1 in norm2 or norm2 in norm1:
                best_score = max(best_score, 0.9)
                continue

            # Fuzzy matching
            ratio = fuzz.ratio(norm1, norm2) / 100
            token_sort = fuzz.token_sort_ratio(norm1, norm2) / 100
            token_set = fuzz.token_set_ratio(norm1, norm2) / 100

            score = max(ratio, token_sort, token_set)
            best_score = max(best_score, score)

        return best_score

    async def find_candidates_by_text(
        self,
        title: str,
        songwriter: str,
        limit: int = 20
    ) -> List[Tuple[Work, Dict[str, float]]]:
        """Find candidate matches using trigram similarity."""
        normalized_title = self.normalize_text(title)

        # Use PostgreSQL trigram similarity
        query = text("""
            SELECT w.*,
                   similarity(w.title_normalized, :title) as title_sim,
                   (
                       SELECT MAX(similarity(sw, :songwriter))
                       FROM unnest(w.songwriters_normalized) as sw
                   ) as songwriter_sim
            FROM works w
            WHERE similarity(w.title_normalized, :title) > 0.3
               OR w.title_normalized LIKE :title_pattern
            ORDER BY similarity(w.title_normalized, :title) DESC
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "title": normalized_title,
                "songwriter": self.normalize_text(songwriter),
                "title_pattern": f"%{normalized_title}%",
                "limit": limit
            }
        )
        rows = result.fetchall()

        candidates = []
        for row in rows:
            work = await self.db.get(Work, row.id)
            if work:
                candidates.append((work, {
                    "title": float(row.title_sim or 0),
                    "songwriter": float(row.songwriter_sim or 0)
                }))

        return candidates

    async def find_candidates_by_vector(
        self,
        usage_record: UsageRecord,
        limit: int = 10
    ) -> List[Tuple[Work, float]]:
        """Find candidate matches using vector similarity."""
        if usage_record.title_embedding is None:
            return []

        # Use pgvector cosine similarity
        query = text("""
            SELECT id, 1 - (combined_embedding <=> :embedding) as similarity
            FROM works
            WHERE combined_embedding IS NOT NULL
            ORDER BY combined_embedding <=> :embedding
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "embedding": str(list(usage_record.title_embedding)),
                "limit": limit
            }
        )
        rows = result.fetchall()

        candidates = []
        for row in rows:
            work = await self.db.get(Work, row.id)
            if work:
                candidates.append((work, float(row.similarity)))

        return candidates

    async def match_usage_record(
        self,
        usage_record: UsageRecord
    ) -> List[MatchResult]:
        """Match a single usage record against the works database."""
        title = usage_record.work_title or usage_record.recording_title
        songwriter = usage_record.songwriter or ""

        # Get candidates from text-based search
        text_candidates = await self.find_candidates_by_text(title, songwriter)

        # Get candidates from vector search
        vector_candidates = await self.find_candidates_by_vector(usage_record)

        # Merge candidates
        work_scores: Dict[int, Dict] = {}

        for work, scores in text_candidates:
            work_scores[work.id] = {
                "work": work,
                "title_sim": scores["title"],
                "songwriter_sim": scores["songwriter"],
                "vector_sim": 0.0
            }

        for work, vector_sim in vector_candidates:
            if work.id in work_scores:
                work_scores[work.id]["vector_sim"] = vector_sim
            else:
                work_scores[work.id] = {
                    "work": work,
                    "title_sim": self.calculate_title_similarity(title, work.title),
                    "songwriter_sim": self.calculate_songwriter_similarity(songwriter, work.songwriters),
                    "vector_sim": vector_sim
                }

        # Score and classify candidates
        matches = []
        ambiguous_candidates = []

        for work_id, data in work_scores.items():
            work = data["work"]
            title_sim = data["title_sim"]
            songwriter_sim = data["songwriter_sim"]
            vector_sim = data["vector_sim"]

            # Calculate combined confidence score
            # Weight: title 40%, songwriter 30%, vector 30%
            confidence = (
                title_sim * 0.4 +
                songwriter_sim * 0.3 +
                vector_sim * 0.3
            )

            # Boost if both title and songwriter match well
            if title_sim > 0.8 and songwriter_sim > 0.7:
                confidence = min(1.0, confidence * 1.1)

            # Determine match type
            if confidence >= settings.exact_match_threshold:
                match_type = "exact"
            elif confidence >= settings.high_confidence_threshold:
                match_type = "high_confidence"
            elif confidence >= settings.medium_confidence_threshold:
                match_type = "medium_confidence"
                # Add to ambiguous for AI review
                if settings.use_ai_for_ambiguous:
                    ambiguous_candidates.append({
                        "work": work,
                        "confidence": confidence,
                        "title_sim": title_sim,
                        "songwriter_sim": songwriter_sim,
                        "vector_sim": vector_sim
                    })
            elif confidence >= settings.low_confidence_threshold:
                match_type = "low_confidence"
            else:
                continue  # Skip low confidence matches

            match = MatchResult(
                usage_record_id=usage_record.id,
                work_id=work.id,
                confidence_score=round(confidence, 4),
                match_type=match_type,
                title_similarity=round(title_sim, 4),
                songwriter_similarity=round(songwriter_sim, 4),
                vector_similarity=round(vector_sim, 4)
            )
            matches.append(match)

        # Use AI to review ambiguous matches
        if ambiguous_candidates and settings.use_ai_for_ambiguous:
            for candidate in ambiguous_candidates[:settings.ai_batch_size]:
                work = candidate["work"]
                ai_result = await self.ollama_service.reason_about_match(
                    usage_title=title,
                    usage_songwriter=songwriter,
                    work_title=work.title,
                    work_songwriters=work.songwriters,
                    similarity_scores={
                        "title": candidate["title_sim"],
                        "songwriter": candidate["songwriter_sim"],
                        "vector": candidate["vector_sim"]
                    }
                )

                # Update match with AI reasoning
                for match in matches:
                    if match.work_id == work.id:
                        if ai_result["is_match"] and ai_result["confidence"] > 0.7:
                            match.match_type = "ai_matched"
                            match.confidence_score = max(
                                float(match.confidence_score),
                                ai_result["confidence"]
                            )
                        match.ai_reasoning = ai_result["reasoning"]
                        break

        return matches

    async def process_batch(
        self,
        usage_records: List[UsageRecord],
        progress_callback=None
    ) -> Dict:
        """Process a batch of usage records."""
        results = {
            "matched": 0,
            "unmatched": 0,
            "flagged": 0,
            "total": len(usage_records)
        }

        for i, record in enumerate(usage_records):
            matches = await self.match_usage_record(record)

            if matches:
                # Save all matches
                for match in matches:
                    self.db.add(match)

                best_match = max(matches, key=lambda m: float(m.confidence_score))

                if best_match.match_type in ["exact", "high_confidence", "ai_matched"]:
                    results["matched"] += 1
                else:
                    results["flagged"] += 1
            else:
                results["unmatched"] += 1

            if progress_callback:
                await progress_callback(i + 1, results)

        await self.db.commit()
        return results
