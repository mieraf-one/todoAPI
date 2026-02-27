from pydantic import BaseModel
from datetime import datetime


class SignupCreate(BaseModel):
    first_name: str
    last_name: str | None = None
    username: str
    password: str
    confirm_password: str

class SignupResponse(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginCreate(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    access_type: str
    refresh_token: str

class UserCardResponse(BaseModel):
    id: int
    username: str
