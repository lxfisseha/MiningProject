from fastapi import UploadFile, Request
from sqlmodel import Session
from abc import abstractmethod, ABC

from src.auth.models import User

from .storage import FileStorageService
from .services import DocumentService
from .models import DocumentType, DocumentReviewStatus
from .schemas import DocumentCreateRequest



document_services = DocumentService(FileStorageService())

class ProfileDocumentsService(ABC):
    @abstractmethod
    def save_profile_documents(self, form_data: dict, session: Session, actor: User):
        pass

class LicenseHolderProfileDocumentsService(ProfileDocumentsService):
    geological_report_document: UploadFile|None
    geological_report_document_request: DocumentCreateRequest

    license_certificate_document: UploadFile|None
    license_certificate_document_request: DocumentCreateRequest

    national_id_document: UploadFile|None
    national_id_document_request: DocumentCreateRequest

    async def save_profile_documents(self, form_data: dict, session: Session, actor: User):
        self._fetch_uploaded_documents(form_data)
        self._create_document_request(actor)
        self._save_files(session)


        print("Fetched the following documents: ")
        print(self.geological_report_document)
        print(self.license_certificate_document)
        print(self.national_id_document)

        print("Created These Requests")
        print(self.geological_report_document_request)
        print(self.license_certificate_document_request)
        print(self.national_id_document_request)


    async def _fetch_uploaded_documents(self, data: dict):
        docs = data.get("license_holder_profile", None)
        if docs is None:
            return 

        self.geological_report_document = docs.get("geological_report_document", None)
        self.license_certificate_document = docs.get("license_certificate_document", None)
        self.national_id_document = docs.get("national_id_document", None)

    def _create_document_request(self, actor: User):
        if self.geological_report_document is not None:
            self.geological_report_document_request = DocumentCreateRequest(
                uploaded_by= actor.id,
                document_type=DocumentType.GEOLOGICAL_REPORT,
                subdir="geological_reports"
            )
        if self.license_certificate_document is not None:
            self.license_certificate_document_request = DocumentCreateRequest(
                uploaded_by=actor.id,
                document_type=DocumentType.LICENSE_CERTIFICATE,
                subdir="license_certificates"
            )
        if self.national_id_document is not None:
            self.national_id_document_request = DocumentCreateRequest(
                uploaded_by=actor.id,
                document_type=DocumentType.NATIONAL_ID,
                subdir="national_ids"
            )
        
        return 1

    async def _save_files(self, session: Session):
        if self.geological_report_document:
            document_services.create_document(
                session,
                self.geological_report_document,
                self.geological_report_document_request
            )
        if self.license_certificate_document:
            document_services.create_document(
                session,
                self.license_certificate_document,
                self.license_certificate_document_request
            )
        if self.national_id_document:
            document_services.create_document(
                session,
                self.national_id_document,
                self.national_id_document_request
            )
        return 1
    
