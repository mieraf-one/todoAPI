from datetime import datetime

from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    content: str

class TodoUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_done: bool | None = None
 
class TodoResponse(BaseModel):
    id: int
    owner_username: str
    title: str
    content: str
    is_done: bool
    created_at: datetime
    
    class Config:
        from_attributes = True