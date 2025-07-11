from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    apprentice = "apprentice"
    mentor = "mentor"
    admin = "admin"

class UserCreate(BaseModel):
    name: str
    email: str
    role: RoleEnum

    @validator("role")
    def validate_role(cls, value):
        if value not in ["mentor", "apprentice"]:
            raise ValueError("Role must be either 'mentor' or 'apprentice'")
        return value

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: RoleEnum

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: str
    name: str
    email: str
    role: RoleEnum