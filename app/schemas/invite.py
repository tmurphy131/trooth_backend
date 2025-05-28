from pydantic import BaseModel, EmailStr

class InviteCreate(BaseModel):
    apprentice_email: EmailStr
    apprentice_name: str
    mentor_id: str

class InviteAccept(BaseModel):
    token: str
    apprentice_id: str