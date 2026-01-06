from fastapi import APIRouter
from app.api import upload, batches, matches, works, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(batches.router, prefix="/batches", tags=["batches"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(works.router, prefix="/works", tags=["works"])
