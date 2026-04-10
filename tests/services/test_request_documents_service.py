import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID, uuid4
from sqlmodel import Session

from src.documents.request_documents import RequestDocumentsService, get_docs_config_for_request_type, get_are_docs_required, get_request_documents_service, DocumentConfig
from src.documents.services import DocumentService
from src.documents.models import DocumentType
from src.documents.schemas import DocumentCreateRequest
from src.documents.exceptions import (
    MissingDocumentsError, UnexpectedDocumentError, MissingRequiredDocumentError,
    InvalidFileTypeError, FileHasNoNameError, UnableToSaveDocumentError,
    UnableToCreateDocumentRecordError, InvalidprofileFieldError
)
from src.auth.models import User
from src.requests.enums import RequestType
from src.requests.models import Request


@pytest.fixture
def mock_document_service():
    service = Mock(spec=DocumentService)
    service.storage = Mock()
    return service


@pytest.fixture
def request_documents_service(mock_document_service):
    return RequestDocumentsService(document_service=mock_document_service)


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.request_type = RequestType.CONSULTING
    return request


@pytest.fixture
def mock_request_detail():
    # Use a simple object for request_detail
    class RequestDetail:
        pass
    return RequestDetail()


@pytest.fixture
def mock_upload_file():
    file = Mock()
    file.filename = "test.pdf"
    file.content_type = "application/pdf"
    return file


@pytest.fixture
def mock_file_save_response():
    return Mock(file_path="uploads/test/test.pdf")


@pytest.fixture
def mock_document_record():
    doc = Mock()
    doc.id = uuid4()
    return doc


class TestRequestDocumentsService:
    def test_init(self, mock_document_service):
        service = RequestDocumentsService(mock_document_service)
        assert service.document_service == mock_document_service

    @pytest.mark.asyncio
    async def test_save_request_documents_success(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user, mock_upload_file, mock_file_save_response, mock_document_record):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        request_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        request_documents_service.document_service.create_document_record = Mock(return_value=mock_document_record)
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Ensure request_detail has the required attribute
        mock_request_detail.license_certificate_document_id = None

        # Act
        await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

        # Assert
        request_documents_service.document_service.save_document.assert_called_once()
        request_documents_service.document_service.create_document_record.assert_called_once()
        assert hasattr(mock_request_detail, 'license_certificate_document_id')
        mock_session.add.assert_called_with(mock_request_detail)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_request_documents_missing_documents_required(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user):
        # Arrange
        form_data = {}
        mock_request.request_type = RequestType.CONSULTING  # Requires docs

        # Act & Assert
        with pytest.raises(MissingDocumentsError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

    @pytest.mark.asyncio
    async def test_save_request_documents_missing_documents_not_required(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user):
        # Arrange
        form_data = {"documents": {}}
        mock_request.request_type = RequestType.MINERAL_BUYER  # No docs required
        mock_session.add = Mock()
        mock_session.commit = Mock()

        # Act
        await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

        # Assert
        mock_session.add.assert_called_with(mock_request_detail)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_request_documents_unexpected_fields(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user):
        # Arrange
        form_data = {
            "documents": {
                "unexpected_field": Mock()
            }
        }

        # Act & Assert
        with pytest.raises(UnexpectedDocumentError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

    @pytest.mark.asyncio
    async def test_save_request_documents_missing_required(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": None
            }
        }
        mock_request.request_type = RequestType.CONSULTING

        # Act & Assert
        with pytest.raises(UnableToSaveDocumentError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

    @pytest.mark.asyncio
    async def test_save_request_documents_save_failure(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user, mock_upload_file):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        exc = Exception("Save failed")
        exc.detail = "Storage error"
        request_documents_service.document_service.save_document = AsyncMock(side_effect=exc)
        request_documents_service._cleanup_files = AsyncMock()

        # Act & Assert
        with pytest.raises(UnableToSaveDocumentError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

        request_documents_service._cleanup_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_request_documents_record_creation_failure(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user, mock_upload_file, mock_file_save_response):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        request_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        request_documents_service.document_service.create_document_record = Mock(side_effect=Exception("Record creation failed"))
        request_documents_service._cleanup_files = AsyncMock()
        mock_session.rollback = Mock()
        mock_request_detail.license_certificate_document_id = None

        # Act & Assert
        with pytest.raises(UnableToCreateDocumentRecordError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

        mock_session.rollback.assert_called_once()
        request_documents_service._cleanup_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_request_documents_invalid_request_field(self, request_documents_service, mock_session, mock_request, mock_request_detail, mock_user, mock_upload_file, mock_file_save_response, mock_document_record):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        request_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        request_documents_service.document_service.create_document_record = Mock(return_value=mock_document_record)
        # request_detail does not have the attribute

        # Act & Assert
        with pytest.raises(UnableToCreateDocumentRecordError):
            await request_documents_service.save_request_documents(form_data, mock_session, mock_request, mock_request_detail, mock_user)

    @pytest.mark.asyncio
    async def test_cleanup_files(self, request_documents_service):
        # Arrange
        file_paths = ["path1", "path2"]
        request_documents_service.document_service.storage.delete_file_by_path = AsyncMock()

        # Act
        await request_documents_service._cleanup_files(file_paths)

        # Assert
        assert request_documents_service.document_service.storage.delete_file_by_path.call_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_files_with_exception(self, request_documents_service):
        # Arrange
        file_paths = ["path1", "path2"]
        request_documents_service.document_service.storage.delete_file_by_path = AsyncMock(side_effect=Exception("Delete failed"))

        # Act
        await request_documents_service._cleanup_files(file_paths)

        # Assert
        # Should not raise exception

    def test_validate_file_valid(self, request_documents_service, mock_upload_file):
        # Act & Assert
        request_documents_service._validate_file(mock_upload_file)  # Should not raise

    def test_validate_file_invalid_type(self, request_documents_service):
        # Arrange
        mock_upload_file = Mock()
        mock_upload_file.content_type = "text/plain"
        mock_upload_file.filename = "test.txt"

        # Act & Assert
        with pytest.raises(InvalidFileTypeError):
            request_documents_service._validate_file(mock_upload_file)

    def test_validate_file_no_filename(self, request_documents_service):
        # Arrange
        mock_upload_file = Mock()
        mock_upload_file.content_type = "application/pdf"
        mock_upload_file.filename = None

        # Act & Assert
        with pytest.raises(FileHasNoNameError):
            request_documents_service._validate_file(mock_upload_file)


class TestHelperFunctions:
    def test_get_docs_config_for_request_type_consulting(self):
        config = get_docs_config_for_request_type(RequestType.CONSULTING)
        assert "license_certificate_document" in config
        assert config["license_certificate_document"].required is True
        assert config["license_certificate_document"].type == DocumentType.LICENSE_CERTIFICATE

    def test_get_docs_config_for_request_type_mineral_seller(self):
        config = get_docs_config_for_request_type(RequestType.MINERAL_SELLER)
        assert "license_certificate_document" in config
        assert config["license_certificate_document"].required is True

    def test_get_docs_config_for_request_type_license_sell(self):
        config = get_docs_config_for_request_type(RequestType.LICENSE_SELL)
        assert "license_certificate_document" in config
        assert "geological_report_document" in config
        assert config["license_certificate_document"].required is True
        assert config["geological_report_document"].required is True

    def test_get_docs_config_for_request_type_mineral_buyer(self):
        config = get_docs_config_for_request_type(RequestType.MINERAL_BUYER)
        assert config == {}

    def test_get_docs_config_for_request_type_unknown(self):
        config = get_docs_config_for_request_type("UNKNOWN_TYPE")
        assert config == {}

    def test_get_are_docs_required_true(self):
        assert get_are_docs_required(RequestType.CONSULTING) is True

    def test_get_are_docs_required_false(self):
        assert get_are_docs_required(RequestType.MINERAL_BUYER) is False

    def test_get_request_documents_service(self, mock_document_service):
        service = get_request_documents_service(mock_document_service)
        assert isinstance(service, RequestDocumentsService)
        assert service.document_service == mock_document_service