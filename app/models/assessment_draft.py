from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Boolean
from app.db import Base
from datetime import datetime
import uuid

class AssessmentDraft(Base):
    __tablename__ = "assessment_drafts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apprentice_id = Column(String, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=True)  # Partial answers
    last_question_id = Column(String, nullable=True)  # Track last interacted question
    is_submitted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
