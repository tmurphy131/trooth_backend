from pydantic import BaseModel
from typing import Optional, Dict, List

class QuestionItem(BaseModel):
    id: str
    text: str
    category_id: str

    class Config:
        from_attributes = True

class AssessmentDraftCreate(BaseModel):
    answers: Optional[Dict[str, str]]
    last_question_id: Optional[str]
    template_id: str

class AssessmentDraftUpdate(BaseModel):
    last_question_id: Optional[str]
    answers: Optional[Dict[str, str]]

class AssessmentDraftOut(BaseModel):
    id: str
    apprentice_id: str
    template_id: str
    answers: Optional[Dict[str, str]]
    last_question_id: Optional[str]
    is_submitted: bool
    questions: List[QuestionItem]

    class Config:
        from_attributes = True

class AssessmentAnswerOut(BaseModel):
    question_id: str
    answer_text: Optional[str]

    class Config:
        from_attributes = True
