from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    usage_record_id = Column(Integer, ForeignKey("usage_records.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    match_type = Column(String(50), nullable=False)  # 'exact', 'high_confidence', 'medium_confidence', 'low_confidence', 'ai_matched'
    title_similarity = Column(Numeric(5, 4))
    songwriter_similarity = Column(Numeric(5, 4))
    vector_similarity = Column(Numeric(5, 4))
    ai_reasoning = Column(Text)
    is_confirmed = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    reviewed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    usage_record = relationship("UsageRecord", back_populates="matches")
    work = relationship("Work", back_populates="matches")
