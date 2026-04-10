from dataclasses import dataclass
from typing import Any, Dict
from fastapi import UploadFile
from sqlmodel import Session

from src.auth.models import User
from src.documents.exceptions import FileHasNoNameError, InvalidFileTypeError, InvalidRequestFieldError, MissingDocumentsError, MissingRequiredDocumentError, UnableToCreateDocumentRecordError, UnableToSaveDocumentError, UnexpectedDocumentError
from src.documents.models import DocumentType
from src.documents.schemas import DocumentCreateRequest
from src.documents.services import DocumentService
from src.requests.enums import RequestType
from src.requests.models import Request

@dataclass
class DocumentConfig:
    type: DocumentType
    request_field_name: str
    required: bool = False

REQUEST_TYPE_TO_DOCS_CONFIG = {
    RequestType.CONSULTING: {
        "license_certificate_document": DocumentConfig(
            type=DocumentType.LICENSE_CERTIFICATE,
            request_field_name="license_certificate_document_id",
            required=True
        )
    },
    RequestType.MINERAL_SELLER: {
        "license_certificate_document": DocumentConfig(
            type=DocumentType.LICENSE_CERTIFICATE,
            request_field_name="license_certificate_document_id",
            required=True
        )
    },
    RequestType.LICENSE_SELL: {
        "license_certificate_document": DocumentConfig(
            type=DocumentType.LICENSE_CERTIFICATE,
            request_field_name="license_certificate_document_id",
            required=True
        ),
        "geological_report_document": DocumentConfig(
            type=DocumentType.GEOLOGICAL_REPORT,
            request_field_name="geological_report_document_id",
            required=True
        ),
    },
    RequestType.MINERAL_BUYER: {

    }
}

def get_docs_config_for_request_type(request_type: RequestType) -> Dict[str, DocumentConfig]:
    return REQUEST_TYPE_TO_DOCS_CONFIG.get(request_type, {})

def get_are_docs_required(request_type: RequestType)->bool:
    config_dict = get_docs_config_for_request_type(request_type)
    for field, config in config_dict.items():
        if config.required:
            return True
    return False

class RequestDocumentsService():
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def save_request_documents(
        self,
        form_data: Dict[str, Any],
        session: Session,
        request: Request,
        request_detail: Any,
        actor: User,
    ) -> None:
        docs = form_data.get("documents", [])
        config_dict = get_docs_config_for_request_type(request.request_type)

        if not docs and get_are_docs_required(request.request_type):
            raise MissingDocumentsError()


        unexpected_fields = set(docs.keys()) - set(config_dict.keys())
        if unexpected_fields:
                raise UnexpectedDocumentError(unexpected_fields)
        
        saved_files = []

        for field_name, config in config_dict.items():
            print("here are the docs we found: ", docs)
            file: UploadFile | None = docs.get(field_name)
            sub_dir = config.type.value.lower() + "s"
            try:
                if not file and config.required:
                    raise MissingRequiredDocumentError(field_name)

                if not file:
                    continue

                self._validate_file(file)
            
                saved_file = await self.document_service.save_document(file, sub_dir)
                saved_files.append((saved_file, config))
            except Exception as e: 
                await self._cleanup_files([f.file_path for f, _ in saved_files])
                msg = e.detail or ""
                raise UnableToSaveDocumentError(f"Failed to save file for {field_name}. {e}")

        for saved_file, config in saved_files:
            try:
                document_record = self.document_service.create_document_record(
                    session=session,
                    file_save_response=saved_file,
                    data=DocumentCreateRequest(
                        uploaded_by=actor.id,
                        document_type=config.type
                    )
                )
                if not hasattr(request_detail, config.request_field_name):
                    raise InvalidRequestFieldError(config.request_field_name)
                setattr(request_detail, config.request_field_name, document_record.id)
            
            except Exception as e:
                session.rollback()
                await self._cleanup_files([f.file_path for f, _ in saved_files])
                raise UnableToCreateDocumentRecordError(f"Failed to create document records: {str(e)}")

        session.add(request_detail)
        session.commit()

    async def _cleanup_files(self, file_paths: list[str]):
        for path in file_paths:
            try:
                await self.document_service.storage.delete_file_by_path(path)
            except Exception:
                pass

    def _validate_file(self, file: UploadFile) -> None:
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]

        if file.content_type not in allowed_types:
            raise InvalidFileTypeError(file.content_type)
        
        if not file.filename:
            raise FileHasNoNameError()

    def get_request_documents(self, request: Request, request_detail: Any, session: Session):
        config_dict = get_docs_config_for_request_type(request.request_type)
        doc_ids = []
        for field_name, config in config_dict.items():
            if hasattr(request_detail, config.request_field_name):
                doc_ids.append(getattr(request_detail, config.request_field_name))
        return self.document_service.get_documents_by_ids(session, doc_ids)




def get_request_documents_service(
    document_service: DocumentService,
) -> RequestDocumentsService:
    return RequestDocumentsService(document_service)
