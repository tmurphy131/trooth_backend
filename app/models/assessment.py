from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from app.db import Base
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apprentice_id = Column(String, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=True)
    recommendation = Column(String, nullable=True)
    category = Column(String, nullable=True)
    mentor_notes = relationship("MentorNote", back_populates="assessment", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=datetime.utcnow)

score_history = relationship(
    "AssessmentScoreHistory",
    back_populates="assessment",
    order_by="desc(AssessmentScoreHistory.scored_at)",
    cascade="all, delete-orphan"
)

@hybrid_property
def latest_score(self):
    return self.score_history[0] if self.score_history else None