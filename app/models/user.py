from sqlalchemy import Column, String, DateTime, Enum
import enum
from datetime import datetime
from app.db import Base
import uuid
from sqlalchemy.orm import relationship

class UserRole(enum.Enum):
    apprentice = "apprentice"
    mentor = "mentor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")