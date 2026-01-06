from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.services.ollama import OllamaService

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including dependencies."""
    status = {
        "api": "healthy",
        "database": "unknown",
        "ollama": "unknown"
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"

    # Check Ollama
    try:
        ollama = OllamaService()
        if await ollama.check_connection():
            status["ollama"] = "healthy"
        else:
            status["ollama"] = "unhealthy: connection failed"
    except Exception as e:
        status["ollama"] = f"unhealthy: {str(e)}"

    overall = "healthy" if all(
        v == "healthy" for v in status.values()
    ) else "degraded"

    return {"status": overall, "services": status}
