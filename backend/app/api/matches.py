from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import datetime
import csv
import io
from app.core.database import get_db
from app.models import MatchResult, UsageRecord, Work

router = APIRouter()


class WorkInfo(BaseModel):
    id: int
    work_code: str
    title: str
    songwriters: List[str]
    iswc: Optional[str] = None

    class Config:
        from_attributes = True


class UsageInfo(BaseModel):
    id: int
    recording_title: Optional[str] = None
    recording_artist: Optional[str] = None
    work_title: Optional[str] = None
    songwriter: Optional[str] = None
    row_number: int

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    usage_record: UsageInfo
    work: WorkInfo
    confidence_score: float
    match_type: str
    title_similarity: Optional[float] = None
    songwriter_similarity: Optional[float] = None
    vector_similarity: Optional[float] = None
    ai_reasoning: Optional[str] = None
    is_confirmed: bool
    is_rejected: bool
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    matches: List[MatchResponse]
    total: int
    page: int
    page_size: int


class ReviewRequest(BaseModel):
    action: str  # 'confirm' or 'reject'


@router.get("/batch/{batch_id}", response_model=MatchListResponse)
async def list_batch_matches(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    match_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    reviewed: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all matches for a batch."""
    # Build query
    query = (
        select(MatchResult)
        .join(UsageRecord)
        .where(UsageRecord.batch_id == batch_id)
        .options(selectinload(MatchResult.usage_record), selectinload(MatchResult.work))
        .order_by(MatchResult.confidence_score.desc())
    )

    if match_type:
        query = query.where(MatchResult.match_type == match_type)

    if min_confidence is not None:
        query = query.where(MatchResult.confidence_score >= min_confidence)

    if reviewed is not None:
        if reviewed:
            query = query.where(
                (MatchResult.is_confirmed == True) | (MatchResult.is_rejected == True)
            )
        else:
            query = query.where(
                and_(MatchResult.is_confirmed == False, MatchResult.is_rejected == False)
            )

    # Count total
    count_query = (
        select(func.count(MatchResult.id))
        .join(UsageRecord)
        .where(UsageRecord.batch_id == batch_id)
    )
    if match_type:
        count_query = count_query.where(MatchResult.match_type == match_type)
    if min_confidence is not None:
        count_query = count_query.where(MatchResult.confidence_score >= min_confidence)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    matches = result.scalars().all()

    return MatchListResponse(
        matches=[
            MatchResponse(
                id=m.id,
                usage_record=UsageInfo(
                    id=m.usage_record.id,
                    recording_title=m.usage_record.recording_title,
                    recording_artist=m.usage_record.recording_artist,
                    work_title=m.usage_record.work_title,
                    songwriter=m.usage_record.songwriter,
                    row_number=m.usage_record.row_number
                ),
                work=WorkInfo(
                    id=m.work.id,
                    work_code=m.work.work_code,
                    title=m.work.title,
                    songwriters=m.work.songwriters,
                    iswc=m.work.iswc
                ),
                confidence_score=float(m.confidence_score),
                match_type=m.match_type,
                title_similarity=float(m.title_similarity) if m.title_similarity else None,
                songwriter_similarity=float(m.songwriter_similarity) if m.songwriter_similarity else None,
                vector_similarity=float(m.vector_similarity) if m.vector_similarity else None,
                ai_reasoning=m.ai_reasoning,
                is_confirmed=m.is_confirmed,
                is_rejected=m.is_rejected,
                reviewed_at=m.reviewed_at,
                created_at=m.created_at
            )
            for m in matches
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/unmatched/{batch_id}")
async def list_unmatched(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List usage records with no matches."""
    # Subquery to find records with matches
    matched_ids = (
        select(MatchResult.usage_record_id)
        .distinct()
    )

    query = (
        select(UsageRecord)
        .where(
            and_(
                UsageRecord.batch_id == batch_id,
                ~UsageRecord.id.in_(matched_ids)
            )
        )
        .order_by(UsageRecord.row_number)
    )

    # Count
    count_query = (
        select(func.count(UsageRecord.id))
        .where(
            and_(
                UsageRecord.batch_id == batch_id,
                ~UsageRecord.id.in_(matched_ids)
            )
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "records": [
            {
                "id": r.id,
                "recording_title": r.recording_title,
                "recording_artist": r.recording_artist,
                "work_title": r.work_title,
                "songwriter": r.songwriter,
                "row_number": r.row_number
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/{match_id}/review")
async def review_match(
    match_id: int,
    review: ReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Confirm or reject a match."""
    match = await db.get(MatchResult, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if review.action == "confirm":
        match.is_confirmed = True
        match.is_rejected = False
    elif review.action == "reject":
        match.is_confirmed = False
        match.is_rejected = True
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'confirm' or 'reject'")

    match.reviewed_at = datetime.utcnow()
    await db.commit()

    return {"message": f"Match {review.action}ed successfully"}


@router.get("/export/{batch_id}/unmatched")
async def export_unmatched(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Export unmatched records as CSV."""
    # Get unmatched records
    matched_ids = select(MatchResult.usage_record_id).distinct()

    query = (
        select(UsageRecord)
        .where(
            and_(
                UsageRecord.batch_id == batch_id,
                ~UsageRecord.id.in_(matched_ids)
            )
        )
        .order_by(UsageRecord.row_number)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Row Number",
        "Recording Title",
        "Recording Artist",
        "Work Title",
        "Songwriter"
    ])

    for record in records:
        writer.writerow([
            record.row_number,
            record.recording_title or "",
            record.recording_artist or "",
            record.work_title or "",
            record.songwriter or ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=unmatched_{batch_id}.csv"
        }
    )


@router.get("/export/{batch_id}/flagged")
async def export_flagged(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Export flagged (medium/low confidence) matches as CSV."""
    query = (
        select(MatchResult)
        .join(UsageRecord)
        .where(
            and_(
                UsageRecord.batch_id == batch_id,
                MatchResult.match_type.in_(["medium_confidence", "low_confidence"]),
                MatchResult.is_confirmed == False,
                MatchResult.is_rejected == False
            )
        )
        .options(selectinload(MatchResult.usage_record), selectinload(MatchResult.work))
        .order_by(MatchResult.confidence_score.desc())
    )

    result = await db.execute(query)
    matches = result.scalars().all()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Row Number",
        "Usage Title",
        "Usage Songwriter",
        "Matched Work Code",
        "Matched Work Title",
        "Matched Songwriters",
        "Confidence Score",
        "Match Type",
        "AI Reasoning"
    ])

    for match in matches:
        writer.writerow([
            match.usage_record.row_number,
            match.usage_record.work_title or match.usage_record.recording_title,
            match.usage_record.songwriter or "",
            match.work.work_code,
            match.work.title,
            "; ".join(match.work.songwriters),
            f"{float(match.confidence_score):.2%}",
            match.match_type,
            match.ai_reasoning or ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=flagged_{batch_id}.csv"
        }
    )
