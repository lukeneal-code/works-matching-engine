from sqlalchemy import Column, Integer, String, TIMESTAMP, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recording_title = Column(String(500))
    recording_artist = Column(String(500))
    work_title = Column(String(500))
    work_title_normalized = Column(String(500))
    songwriter = Column(String(500))
    songwriter_normalized = Column(String(500))
    original_row_data = Column(JSON)
    row_number = Column(Integer)
    title_embedding = Column(Vector(768))
    songwriter_embedding = Column(Vector(768))
    created_at = Column(TIMESTAMP, server_default=func.now())

    matches = relationship("MatchResult", back_populates="usage_record", cascade="all, delete-orphan")
