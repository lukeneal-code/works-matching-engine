import json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import get_settings
from app.services.file_processor import FileProcessorService

router = APIRouter()
settings = get_settings()


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a usage file for processing."""

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(('.txt', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Only TXT and CSV files are supported"
        )

    # Read file content
    try:
        content = await file.read()
        # Try to decode as UTF-8, fall back to latin-1
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1')
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )

    # Check file size
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
        )

    # Process file with SSE for progress updates
    processor = FileProcessorService(db)

    async def generate():
        async for update in processor.process_file(content_str, file.filename):
            yield f"data: {json.dumps(update)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/validate")
async def validate_file(
    file: UploadFile = File(...)
):
    """Validate a file without processing it."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(('.txt', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Only TXT and CSV files are supported"
        )

    try:
        content = await file.read()
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1')

        processor = FileProcessorService(None)
        records = processor.parse_file(content_str, file.filename)

        # Get sample of first 5 records
        sample = records[:5] if records else []

        return {
            "valid": True,
            "total_records": len(records),
            "sample_records": sample,
            "detected_columns": list(sample[0].keys()) if sample else []
        }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
