from typing import List
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from src.auth.models import User
from src.documents.models import Document
from src.documents.schemas import DocumentCreateRequest, DocumentResponse
from .schemas import FileReadRequest, FileSaveRequest, FileDeleteRequest
from .storage import FileStorageService
from .models import DocumentType
from uuid import UUID


class DocumentService:
    def __init__(self, storage: FileStorageService):
        self.storage = storage

    async def create_document(
        self,
        session: Session,
        file: UploadFile,
        data: DocumentCreateRequest
    ) -> DocumentResponse:

        subdir = f"{data.document_type.value.lower()}s"

        storage_request = FileSaveRequest(
            filename=file.filename,
            content_type=file.content_type,
            subdir=subdir,
            max_size=5 * 1024 * 1024
        )

        result = await self.storage.save(file, storage_request)

        document = Document(
            uploaded_by=data.uploaded_by,
            document_type=data.document_type,
            file_path=result.file_path,
        )

        session.add(document)
        session.commit()
        session.refresh(document)

        return DocumentResponse(**document.model_dump())

    async def create_documents(
        self,
        db: Session,
        files: List[UploadFile],
        data: DocumentCreateRequest
    ) -> List[DocumentResponse]:

        documents = []

        for file in files:
            doc = await self.create_document(db, file, data)
            documents.append(doc)

        return documents

    def get_documents_by_type(
        self,
        db: Session,
        document_type: DocumentType,
    ) -> List[DocumentResponse]:

        statement = select(Document).where(
            Document.document_type == document_type
        )

        results = db.exec(statement).all()

        return [DocumentResponse(**doc.model_dump()) for doc in results]

    def delete_document(
        self,
        db: Session,
        document_id: UUID,
        current_user_id: UUID
    ):

        document = db.get(Document, document_id)

        if not document:
            raise HTTPException(404, "Document not found")

        if document.uploaded_by != current_user_id:
            raise HTTPException(403, "Not allowed")

        if document.file_path:
            self.storage.delete(
                FileDeleteRequest(file_path=document.file_path)
            )

        db.delete(document)
        db.commit()
    
    def get_document_file(
        self,
        db: Session,
        document_id: UUID,
        current_user: User
    ):
        document = db.get(Document, document_id)

        if not document:
            raise HTTPException(404, "Document not found")

        if not current_user.is_admin and document.uploaded_by != current_user.id:
            raise HTTPException(403, "Not allowed to access this document")

        if not document.file_path:
            raise HTTPException(404, "File not found")

        file = self.storage.open(
            FileReadRequest(file_path=document.file_path)
        )

        return file, document