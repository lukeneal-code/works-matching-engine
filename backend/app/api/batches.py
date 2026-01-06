from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import ProcessingBatch, UsageRecord, MatchResult

router = APIRouter()


class BatchResponse(BaseModel):
    id: str
    filename: str
    total_records: int
    processed_records: int
    matched_records: int
    unmatched_records: int
    flagged_records: int
    status: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BatchListResponse(BaseModel):
    batches: List[BatchResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=BatchListResponse)
async def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all processing batches."""
    query = select(ProcessingBatch).order_by(ProcessingBatch.created_at.desc())

    if status:
        query = query.where(ProcessingBatch.status == status)

    # Count total
    count_query = select(func.count(ProcessingBatch.id))
    if status:
        count_query = count_query.where(ProcessingBatch.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    batches = result.scalars().all()

    return BatchListResponse(
        batches=[
            BatchResponse(
                id=str(b.id),
                filename=b.filename,
                total_records=b.total_records,
                processed_records=b.processed_records,
                matched_records=b.matched_records,
                unmatched_records=b.unmatched_records,
                flagged_records=b.flagged_records,
                status=b.status,
                error_message=b.error_message,
                started_at=b.started_at,
                completed_at=b.completed_at,
                created_at=b.created_at
            )
            for b in batches
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific batch by ID."""
    batch = await db.get(ProcessingBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return BatchResponse(
        id=str(batch.id),
        filename=batch.filename,
        total_records=batch.total_records,
        processed_records=batch.processed_records,
        matched_records=batch.matched_records,
        unmatched_records=batch.unmatched_records,
        flagged_records=batch.flagged_records,
        status=batch.status,
        error_message=batch.error_message,
        started_at=batch.started_at,
        completed_at=batch.completed_at,
        created_at=batch.created_at
    )


@router.delete("/{batch_id}")
async def delete_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a batch and all associated records."""
    batch = await db.get(ProcessingBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Delete associated usage records (cascades to match results)
    query = select(UsageRecord).where(UsageRecord.batch_id == batch_id)
    result = await db.execute(query)
    usage_records = result.scalars().all()

    for record in usage_records:
        await db.delete(record)

    await db.delete(batch)
    await db.commit()

    return {"message": "Batch deleted successfully"}
