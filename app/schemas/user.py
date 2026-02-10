from pydantic import BaseModel, EmailStr
from ..enums import Grade

class UserBase(BaseModel):
    email: EmailStr
    name: str
    grade: Grade
    institute: str
    city: str
    marketing: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class GoogleAuthRequest(BaseModel):
    token: str

class GoogleCompleteProfile(BaseModel):
    token: str
    grade: Grade
    institute: str
    city: str
    marketing: str