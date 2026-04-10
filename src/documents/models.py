from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

import enum

from src.auth.models import User


class DocumentReviewStatus(str, enum.Enum):
    NEW = "NEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DocumentType(str, enum.Enum):
    LICENSE_CERTIFICATE = "LICENSE_CERTIFICATE"
    GEOLOGICAL_REPORT = "GEOLOGICAL_REPORT"
    NATIONAL_ID = "NATIONAL_ID"
    GOVERNMENT_ID = "GOVERNMENT_ID"
    TRADE_LICENSE = "TRADE_LICENSE"
    PROFESSIONAL_LICENSE = "PROFESSIONAL_LICENSE"
    SUPPORTING_DOCUMENT = "SUPPORTING_DOCUMENT"
    OTHER = "OTHER"

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    uploaded_by: UUID = Field(foreign_key="users.id")

    document_type: DocumentType
    file_path: str|None = None

    status: DocumentReviewStatus = DocumentReviewStatus.NEW

    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship()

