from abc import ABC, abstractmethod
import profile
from typing import Dict, Any

from fastapi import UploadFile
from sqlmodel import Session

from src import config
from src.auth.models import User, UserRole
from src.profiles.services import get_profile_by_user

from .services import DocumentService
from .models import DocumentType
from .schemas import DocumentCreateRequest
from .exceptions import *

from dataclasses import dataclass

@dataclass
class DocumentConfig:
    type: DocumentType
    profile_field_name: str
    required: bool = False

ROLE_DOCUMENT_CONFIGS = {
    UserRole.LICENSE_HOLDER: {
        "geological_report_document": DocumentConfig(
            type=DocumentType.GEOLOGICAL_REPORT,
            profile_field_name="geological_report_document_id"
        ),
        "license_certificate_document": DocumentConfig(
            type= DocumentType.LICENSE_CERTIFICATE,
            profile_field_name="license_certificate_document_id",
            required= True
        ),
        "national_id_document": DocumentConfig(
            type= DocumentType.NATIONAL_ID,
            profile_field_name="national_id_document_id"
        ),
    },
    UserRole.EQUIPMENT_OWNER: {
        "trade_license_document": DocumentConfig(
            type=DocumentType.TRADE_LICENSE,
            profile_field_name="trade_license_document_id"
        ),
        "national_id_document": DocumentConfig(
            type=DocumentType.NATIONAL_ID,
            profile_field_name="national_id_document_id"
        ),
    },
    UserRole.CONSULTANT: {
        "professional_license_document": DocumentConfig(
            type=DocumentType.PROFESSIONAL_LICENSE,
            profile_field_name="professional_license_document_id"
        ),
        "national_id_document": DocumentConfig(
            type=DocumentType.NATIONAL_ID,
            profile_field_name="national_id_document_id"
        ),
        "supporting_document": DocumentConfig(
            type=DocumentType.SUPPORTING_DOCUMENT,
            profile_field_name="supporting_document_id"
        ),
    },
    UserRole.BUYER: {
        "supporting_document": DocumentConfig(
            type=DocumentType.SUPPORTING_DOCUMENT,
            profile_field_name="supporting_document_id"
        ),
    }
}


def get_docs_config_for_role(role: UserRole) -> Dict[str, DocumentConfig]:
    return ROLE_DOCUMENT_CONFIGS.get(role, {})


class ProfileDocumentsService():
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def save_profile_documents(
        self,
        form_data: Dict[str, Any],
        session: Session,
        actor: User,
    ) -> None:
        docs = form_data.get("documents", None)
        profile = get_profile_by_user(actor, session)


        if not docs:
            raise MissingDocumentsError()

        config_dict = get_docs_config_for_role(actor.role)

        unexpected_fields = set(docs.keys()) - set(config_dict.keys())
        if unexpected_fields:
                raise UnexpectedDocumentError(unexpected_fields)
        saved_files = []

        for field_name, config in config_dict.items():
            file: UploadFile | None = docs.get(field_name)
            sub_dir = config.type.value.lower() + "s"

            if not file and config.required:
                raise MissingRequiredDocumentError(field_name)

            if not file:
                continue

            self._validate_file(file)
            try:
                saved_file = await self.document_service.save_document(file, sub_dir)
                saved_files.append((saved_file, config))
            except: 
                self._cleanup_files([f.file_path for f, _ in saved_files])
                raise UnableToSaveDocumentError(f"Failed to save file for {field_name}")

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
                if not hasattr(profile, config.profile_field_name):
                    raise InvalidprofileFieldError(config.profile_field_name)
                setattr(profile, config.profile_field_name, document_record.id)
            
            except Exception as e:
                session.rollback()
                await self._cleanup_files([f.file_path for f, _ in saved_files])
                raise UnableToCreateDocumentRecordError(f"Failed to create document records: {str(e)}")

        session.add(profile)
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

def get_profile_documents_service(
    document_service: DocumentService,
) -> ProfileDocumentsService:
    return ProfileDocumentsService(document_service)