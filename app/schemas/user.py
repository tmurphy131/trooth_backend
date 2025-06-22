from pydantic import BaseModel, validator
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    role: str

    @validator("role")
    def validate_role(cls, value):
        if value not in ["mentor", "apprentice"]:
            raise ValueError("Role must be either 'mentor' or 'apprentice'")
        return value

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
