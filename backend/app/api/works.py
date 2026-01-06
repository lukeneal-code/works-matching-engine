from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Work
from app.services.embedding import EmbeddingService

router = APIRouter()


class WorkCreate(BaseModel):
    work_code: str
    title: str
    alternative_titles: Optional[List[str]] = None
    iswc: Optional[str] = None
    songwriters: List[str]
    publishers: Optional[List[str]] = None
    release_year: Optional[int] = None
    genre: Optional[str] = None


class WorkResponse(BaseModel):
    id: int
    work_code: str
    title: str
    alternative_titles: Optional[List[str]] = None
    iswc: Optional[str] = None
    songwriters: List[str]
    publishers: Optional[List[str]] = None
    release_year: Optional[int] = None
    genre: Optional[str] = None
    has_embedding: bool = False

    class Config:
        from_attributes = True


class WorkListResponse(BaseModel):
    works: List[WorkResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=WorkListResponse)
async def list_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List works with optional search."""
    query = select(Work).order_by(Work.title)

    if search:
        search_lower = f"%{search.lower()}%"
        query = query.where(
            Work.title_normalized.ilike(search_lower) |
            func.array_to_string(Work.songwriters_normalized, ' ').ilike(search_lower)
        )

    # Count
    count_query = select(func.count(Work.id))
    if search:
        search_lower = f"%{search.lower()}%"
        count_query = count_query.where(
            Work.title_normalized.ilike(search_lower) |
            func.array_to_string(Work.songwriters_normalized, ' ').ilike(search_lower)
        )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    works = result.scalars().all()

    return WorkListResponse(
        works=[
            WorkResponse(
                id=w.id,
                work_code=w.work_code,
                title=w.title,
                alternative_titles=w.alternative_titles,
                iswc=w.iswc,
                songwriters=w.songwriters,
                publishers=w.publishers,
                release_year=w.release_year,
                genre=w.genre,
                has_embedding=w.combined_embedding is not None
            )
            for w in works
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{work_id}", response_model=WorkResponse)
async def get_work(
    work_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific work."""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    return WorkResponse(
        id=work.id,
        work_code=work.work_code,
        title=work.title,
        alternative_titles=work.alternative_titles,
        iswc=work.iswc,
        songwriters=work.songwriters,
        publishers=work.publishers,
        release_year=work.release_year,
        genre=work.genre,
        has_embedding=work.combined_embedding is not None
    )


@router.post("", response_model=WorkResponse)
async def create_work(
    work_data: WorkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new work."""
    # Check for duplicate work_code
    existing = await db.execute(
        select(Work).where(Work.work_code == work_data.work_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Work code already exists")

    work = Work(
        work_code=work_data.work_code,
        title=work_data.title,
        alternative_titles=work_data.alternative_titles,
        iswc=work_data.iswc,
        songwriters=work_data.songwriters,
        publishers=work_data.publishers,
        release_year=work_data.release_year,
        genre=work_data.genre
    )

    db.add(work)
    await db.commit()
    await db.refresh(work)

    return WorkResponse(
        id=work.id,
        work_code=work.work_code,
        title=work.title,
        alternative_titles=work.alternative_titles,
        iswc=work.iswc,
        songwriters=work.songwriters,
        publishers=work.publishers,
        release_year=work.release_year,
        genre=work.genre,
        has_embedding=work.combined_embedding is not None
    )


@router.post("/generate-embeddings")
async def generate_embeddings(
    db: AsyncSession = Depends(get_db)
):
    """Generate embeddings for all works that don't have them."""
    embedding_service = EmbeddingService()

    query = select(Work).where(Work.combined_embedding.is_(None))
    result = await db.execute(query)
    works = result.scalars().all()

    if not works:
        return {"message": "All works already have embeddings", "processed": 0}

    processed = 0
    for work in works:
        combined_text = embedding_service.normalize_for_embedding(
            work.title,
            ", ".join(work.songwriters)
        )
        embedding = await embedding_service.get_embedding(combined_text)

        if embedding:
            work.combined_embedding = embedding
            work.title_embedding = await embedding_service.get_embedding(work.title)
            work.songwriter_embedding = await embedding_service.get_embedding(
                ", ".join(work.songwriters)
            )
            processed += 1

    await db.commit()

    return {"message": f"Generated embeddings for {processed} works", "processed": processed}


@router.get("/stats/summary")
async def get_works_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about the works database."""
    total_result = await db.execute(select(func.count(Work.id)))
    total = total_result.scalar() or 0

    with_embedding_result = await db.execute(
        select(func.count(Work.id)).where(Work.combined_embedding.isnot(None))
    )
    with_embedding = with_embedding_result.scalar() or 0

    return {
        "total_works": total,
        "with_embeddings": with_embedding,
        "without_embeddings": total - with_embedding
    }
