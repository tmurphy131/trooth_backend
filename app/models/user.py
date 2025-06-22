from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)  # "mentor" or "apprentice"
    created_at = Column(DateTime, default=datetime.utcnow)