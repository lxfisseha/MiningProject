import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID, uuid4
from sqlmodel import Session

from src.documents.profile_documents import ProfileDocumentsService, get_docs_config_for_role, get_profile_documents_service, DocumentConfig
from src.documents.services import DocumentService
from src.documents.models import DocumentType
from src.documents.schemas import DocumentCreateRequest
from src.documents.exceptions import (
    MissingDocumentsError, UnexpectedDocumentError, MissingRequiredDocumentError,
    InvalidFileTypeError, FileHasNoNameError, UnableToSaveDocumentError,
    UnableToCreateDocumentRecordError, InvalidprofileFieldError
)
from src.auth.models import User, UserRole


@pytest.fixture
def mock_document_service():
    service = Mock(spec=DocumentService)
    service.storage = Mock()
    return service


@pytest.fixture
def profile_documents_service(mock_document_service):
    return ProfileDocumentsService(document_service=mock_document_service)


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = uuid4()
    user.role = UserRole.LICENSE_HOLDER
    return user


@pytest.fixture
def mock_profile():
    # Use a simple object that allows setting attributes
    class Profile:
        pass
    return Profile()


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


class TestProfileDocumentsService:
    def test_init(self, mock_document_service):
        service = ProfileDocumentsService(mock_document_service)
        assert service.document_service == mock_document_service

    @pytest.mark.asyncio
    async def test_save_profile_documents_success(self, profile_documents_service, mock_session, mock_user, mock_profile, mock_upload_file, mock_file_save_response, mock_document_record):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file,
                "national_id_document": mock_upload_file
            }
        }
        config = get_docs_config_for_role(mock_user.role)
        profile_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        profile_documents_service.document_service.create_document_record = Mock(return_value=mock_document_record)
        mock_session.add = Mock()
        mock_session.commit = Mock()
        # Ensure profile has the required attributes
        mock_profile.license_certificate_document_id = None
        mock_profile.national_id_document_id = None

        with patch('src.documents.profile_documents.get_profile_by_user', return_value=mock_profile):
            # Act
            await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

        # Assert
        profile_documents_service.document_service.save_document.assert_called()
        profile_documents_service.document_service.create_document_record.assert_called()
        assert hasattr(mock_profile, 'license_certificate_document_id')
        assert hasattr(mock_profile, 'national_id_document_id')
        mock_session.add.assert_called_with(mock_profile)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_profile_documents_missing_documents(self, profile_documents_service, mock_session, mock_user):
        # Arrange
        form_data = {}

        # Act & Assert
        with pytest.raises(MissingDocumentsError):
            await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

    @pytest.mark.asyncio
    async def test_save_profile_documents_unexpected_fields(self, profile_documents_service, mock_session, mock_user):
        # Arrange
        form_data = {
            "documents": {
                "unexpected_field": Mock()
            }
        }

        # Act & Assert
        with pytest.raises(UnexpectedDocumentError):
            await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

    @pytest.mark.asyncio
    async def test_save_profile_documents_missing_required(self, profile_documents_service, mock_session, mock_user):
        # Arrange
        form_data = {
            "documents": {
                "national_id_document": Mock()
            }
        }

        # Act & Assert
        with pytest.raises(MissingRequiredDocumentError):
            await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

    @pytest.mark.asyncio
    async def test_save_profile_documents_save_failure(self, profile_documents_service, mock_session, mock_user, mock_upload_file):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        profile_documents_service.document_service.save_document = AsyncMock(side_effect=Exception("Save failed"))
        profile_documents_service._cleanup_files = AsyncMock()

        # Act & Assert
        with pytest.raises(UnableToSaveDocumentError):
            await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

        profile_documents_service._cleanup_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_profile_documents_record_creation_failure(self, profile_documents_service, mock_session, mock_user, mock_profile, mock_upload_file, mock_file_save_response):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        profile_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        profile_documents_service.document_service.create_document_record = Mock(side_effect=Exception("Record creation failed"))
        profile_documents_service._cleanup_files = AsyncMock()
        mock_session.rollback = Mock()
        mock_profile.license_certificate_document_id = None

        with patch('src.documents.profile_documents.get_profile_by_user', return_value=mock_profile):
            # Act & Assert
            with pytest.raises(UnableToCreateDocumentRecordError):
                await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

        mock_session.rollback.assert_called_once()
        profile_documents_service._cleanup_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_profile_documents_invalid_profile_field(self, profile_documents_service, mock_session, mock_user, mock_profile, mock_upload_file, mock_file_save_response, mock_document_record):
        # Arrange
        form_data = {
            "documents": {
                "license_certificate_document": mock_upload_file
            }
        }
        profile_documents_service.document_service.save_document = AsyncMock(return_value=mock_file_save_response)
        profile_documents_service.document_service.create_document_record = Mock(return_value=mock_document_record)

        with patch('src.documents.profile_documents.get_profile_by_user', return_value=mock_profile):
            # Act & Assert
            with pytest.raises(UnableToCreateDocumentRecordError):
                await profile_documents_service.save_profile_documents(form_data, mock_session, mock_user)

    @pytest.mark.asyncio
    async def test_cleanup_files(self, profile_documents_service):
        # Arrange
        file_paths = ["path1", "path2"]
        profile_documents_service.document_service.storage.delete_file_by_path = AsyncMock()

        # Act
        await profile_documents_service._cleanup_files(file_paths)

        # Assert
        assert profile_documents_service.document_service.storage.delete_file_by_path.call_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_files_with_exception(self, profile_documents_service):
        # Arrange
        file_paths = ["path1", "path2"]
        profile_documents_service.document_service.storage.delete_file_by_path = AsyncMock(side_effect=Exception("Delete failed"))

        # Act
        await profile_documents_service._cleanup_files(file_paths)

        # Assert
        # Should not raise exception, just continue

    def test_validate_file_valid(self, profile_documents_service, mock_upload_file):
        # Act & Assert
        profile_documents_service._validate_file(mock_upload_file)  # Should not raise

    def test_validate_file_invalid_type(self, profile_documents_service):
        # Arrange
        mock_upload_file = Mock()
        mock_upload_file.content_type = "text/plain"
        mock_upload_file.filename = "test.txt"

        # Act & Assert
        with pytest.raises(InvalidFileTypeError):
            profile_documents_service._validate_file(mock_upload_file)

    def test_validate_file_no_filename(self, profile_documents_service):
        # Arrange
        mock_upload_file = Mock()
        mock_upload_file.content_type = "application/pdf"
        mock_upload_file.filename = None

        # Act & Assert
        with pytest.raises(FileHasNoNameError):
            profile_documents_service._validate_file(mock_upload_file)


class TestHelperFunctions:
    def test_get_docs_config_for_role_license_holder(self):
        config = get_docs_config_for_role(UserRole.LICENSE_HOLDER)
        assert "license_certificate_document" in config
        assert config["license_certificate_document"].required is True
        assert config["license_certificate_document"].type == DocumentType.LICENSE_CERTIFICATE

    def test_get_docs_config_for_role_equipment_owner(self):
        config = get_docs_config_for_role(UserRole.EQUIPMENT_OWNER)
        assert "trade_license_document" in config
        assert config["trade_license_document"].type == DocumentType.TRADE_LICENSE

    def test_get_docs_config_for_role_consultant(self):
        config = get_docs_config_for_role(UserRole.CONSULTANT)
        assert "professional_license_document" in config
        assert config["professional_license_document"].type == DocumentType.PROFESSIONAL_LICENSE

    def test_get_docs_config_for_role_buyer(self):
        config = get_docs_config_for_role(UserRole.BUYER)
        assert "supporting_document" in config
        assert config["supporting_document"].type == DocumentType.SUPPORTING_DOCUMENT

    def test_get_docs_config_for_role_unknown(self):
        config = get_docs_config_for_role("UNKNOWN_ROLE")
        assert config == {}

    def test_get_profile_documents_service(self, mock_document_service):
        service = get_profile_documents_service(mock_document_service)
        assert isinstance(service, ProfileDocumentsService)
        assert service.document_service == mock_document_service