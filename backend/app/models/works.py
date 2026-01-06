from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    work_code = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    title_normalized = Column(String(500), nullable=False)
    alternative_titles = Column(ARRAY(Text))
    iswc = Column(String(20))
    songwriters = Column(ARRAY(Text), nullable=False)
    songwriters_normalized = Column(ARRAY(Text), nullable=False)
    publishers = Column(ARRAY(Text))
    release_year = Column(Integer)
    genre = Column(String(100))
    title_embedding = Column(Vector(768))
    songwriter_embedding = Column(Vector(768))
    combined_embedding = Column(Vector(768))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    matches = relationship("MatchResult", back_populates="work")
