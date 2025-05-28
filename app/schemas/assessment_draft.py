from pydantic import BaseModel
from typing import Optional, Dict

class AssessmentDraftCreate(BaseModel):
    answers: Optional[Dict[str, str]]  # question_id: answer
    last_question_id: Optional[str]  # tracks last interacted question

class AssessmentDraftOut(BaseModel):
    id: str
    apprentice_id: str
    answers: Optional[Dict[str, str]]
    last_question_id: Optional[str]
    is_submitted: bool

    class Config:
        orm_mode = True
