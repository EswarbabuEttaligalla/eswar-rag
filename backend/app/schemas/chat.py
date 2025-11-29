from datetime import datetime
from pydantic import BaseModel


class ChatCreate(BaseModel):
    title: str


class ChatOut(BaseModel):
    id: str
    title: str
    created_at: datetime


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: list
    created_at: datetime
