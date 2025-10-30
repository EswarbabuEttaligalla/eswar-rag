from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    status: str
    metadata: dict
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentOut


class DocumentProcessResponse(BaseModel):
    document_id: str
    status: str
