from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://works_user:works_password@localhost:5432/works_matching"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"

    # Matching thresholds
    exact_match_threshold: float = 0.95
    high_confidence_threshold: float = 0.85
    medium_confidence_threshold: float = 0.70
    low_confidence_threshold: float = 0.50

    # AI matching
    use_ai_for_ambiguous: bool = True
    ai_batch_size: int = 5

    # Processing
    batch_size: int = 100
    max_file_size_mb: int = 50

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
