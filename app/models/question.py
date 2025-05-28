from sqlalchemy import Column, String, ForeignKey
from app.db import Base
import uuid

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)