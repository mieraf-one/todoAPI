from pydantic import BaseModel
from app.schemas import auth as auth_schema
from datetime import datetime

class TodoCreate(BaseModel):
    title: str
    content: str

class TodoUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_done: bool | None = None
 
class TodoResponse(BaseModel):
    id: int
    owner: auth_schema.UserCardResponse
    title: str
    content: str
    is_done: bool
    updated_at: datetime | None
    created_at: datetime
    
    class Config:
        from_attributes = True