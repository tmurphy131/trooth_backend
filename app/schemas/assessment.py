from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime


class AssessmentCreate(BaseModel):
    title: str
    user_id: str
    answers: Dict[str, str]  # e.g., {"Spiritual Growth": "I pray daily", ...}

class AssessmentOut(BaseModel):
    id: str
    apprentice_id: str
    answers: Dict[str, str]
    scores: Optional[Dict[str, int]]
    recommendation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
