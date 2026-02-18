"""
    Pydantic models for authentication-related requests and responses.

    Contains schemas for user registration, login, JWT token responses,
    and the current authenticated user.
"""


from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True