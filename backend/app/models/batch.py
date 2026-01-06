from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class ProcessingBatch(Base):
    __tablename__ = "processing_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    total_records = Column(Integer, nullable=False)
    processed_records = Column(Integer, default=0)
    matched_records = Column(Integer, default=0)
    unmatched_records = Column(Integer, default=0)
    flagged_records = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
