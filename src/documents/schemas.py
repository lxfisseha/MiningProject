from pydantic import BaseModel
from typing import Optional
from .models import DocumentType, Document
from uuid import UUID




class DocumentCreateRequest(BaseModel):
    uploaded_by: UUID
    document_type: DocumentType


class DocumentResponse(BaseModel):
    id: UUID
    document_type: DocumentType
    file_path: str
    status: str
    uploaded_by: UUID

class FileSaveRequest(BaseModel):
    filename: str
    content_type: str
    subdir: Optional[str] = ""
    max_size: Optional[int] = None  # bytes


class FileSaveResponse(BaseModel):
    file_path: str
    file_name: str
    content_type: str
    size: int


class FileDeleteRequest(BaseModel):
    file_path: str


class FileReadRequest(BaseModel):
    file_path: str