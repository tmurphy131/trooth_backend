from pydantic import BaseModel
from typing import Optional, List

class AssessmentTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AssessmentTemplateOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_published: bool

    class Config:
        from_attributes = True

class AddQuestionToTemplate(BaseModel):
    question_id: str
    order: int

class FullTemplateView(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_published: bool
    questions: List[AddQuestionToTemplate]
