from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import uuid

# models/assessment_template.py
class AssessmentTemplate(Base):
    __tablename__ = "assessment_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
