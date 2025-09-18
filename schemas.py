from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PollOptionCreate(BaseModel):
    text: str

class PollOptionResponse(BaseModel):
    id: int
    text: str
    vote_count: int = 0
    
    class Config:
        from_attributes = True

class PollCreate(BaseModel):
    question: str
    options: List[PollOptionCreate]
    is_published: bool = False

class PollResponse(BaseModel):
    id: int
    question: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    creator_id: int
    options: List[PollOptionResponse]
    
    class Config:
        from_attributes = True

class VoteCreate(BaseModel):
    poll_option_id: int

class VoteResponse(BaseModel):
    user_id: int
    poll_option_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True