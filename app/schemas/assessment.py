from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from app.schemas.assessment_score_history import AssessmentScoreHistoryOut


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
    latest_score: Optional[AssessmentScoreHistoryOut] = None

    class Config:
        from_attributes = True
