from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    text: str
    category_id: str

class QuestionOut(BaseModel):
    id: str
    text: str
    category_id: str

    class Config:
        orm_mode = True