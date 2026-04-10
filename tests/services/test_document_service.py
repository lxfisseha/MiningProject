import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID, uuid4
from sqlmodel import Session
from fastapi import UploadFile, HTTPException

from src.documents.services import DocumentService
from src.documents.schemas import DocumentCreateRequest, DocumentResponse, FileSaveRequest, FileSaveResponse, FileDeleteRequest, FileReadRequest
from src.documents.models import Document, DocumentType
from src.auth.models import User


@pytest.fixture
def mock_storage():
    return Mock()


@pytest.fixture
def document_service(mock_storage):
    return DocumentService(storage=mock_storage)


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def mock_upload_file():
    file = Mock(spec=UploadFile)
    file.filename = "test.pdf"
    file.content_type = "application/pdf"
    return file


@pytest.fixture
def mock_file_save_response():
    return FileSaveResponse(
        file_path="uploads/test/test.pdf",
        file_name="test.pdf",
        content_type="application/pdf",
        size=1024
    )


@pytest.fixture
def mock_document():
    return Document(
        id=uuid4(),
        uploaded_by=uuid4(),
        document_type=DocumentType.LICENSE_CERTIFICATE,
        file_path="uploads/test/test.pdf",
        status="NEW"
    )


@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = uuid4()
    user.is_admin = False
    return user


class TestDocumentService:
    def test_init(self, mock_storage):
        service = DocumentService(mock_storage)
        assert service.storage == mock_storage

    @pytest.mark.asyncio
    async def test_save_document_success(self, document_service, mock_upload_file, mock_file_save_response):
        # Arrange
        subdir = "license_certificates"
        document_service.storage.save = AsyncMock(return_value=mock_file_save_response)

        # Act
        result = await document_service.save_document(mock_upload_file, subdir)

        # Assert
        assert result == mock_file_save_response
        document_service.storage.save.assert_called_once_with(
            mock_upload_file,
            FileSaveRequest(
                filename="test.pdf",
                content_type="application/pdf",
                subdir=subdir,
                max_size=5 * 1024 * 1024
            )
        )

    @pytest.mark.asyncio
    async def test_save_document_storage_failure(self, document_service, mock_upload_file):
        # Arrange
        subdir = "license_certificates"
        document_service.storage.save = AsyncMock(side_effect=Exception("Storage error"))

        # Act & Assert
        with pytest.raises(Exception, match="Storage error"):
            await document_service.save_document(mock_upload_file, subdir)

    def test_create_document_record_success(self, document_service, mock_session, mock_file_save_response):
        # Arrange
        data = DocumentCreateRequest(
            uploaded_by=uuid4(),
            document_type=DocumentType.LICENSE_CERTIFICATE
        )
        mock_session.add = Mock()
        mock_session.flush = Mock()

        # Act
        result = document_service.create_document_record(mock_session, mock_file_save_response, data)

        # Assert
        assert isinstance(result, Document)
        assert result.uploaded_by == data.uploaded_by
        assert result.document_type == data.document_type
        assert result.file_path == mock_file_save_response.file_path
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    def test_create_document_record_session_failure(self, document_service, mock_session, mock_file_save_response):
        # Arrange
        data = DocumentCreateRequest(
            uploaded_by=uuid4(),
            document_type=DocumentType.LICENSE_CERTIFICATE
        )
        mock_session.add = Mock(side_effect=Exception("DB error"))

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            document_service.create_document_record(mock_session, mock_file_save_response, data)

    def test_to_response(self, document_service, mock_document):
        # Act
        result = document_service.to_response(mock_document)

        # Assert
        assert isinstance(result, DocumentResponse)
        assert result.id == mock_document.id
        assert result.document_type == mock_document.document_type
        assert result.file_path == mock_document.file_path

    def test_get_documents_by_type_success(self, document_service, mock_session, mock_document):
        # Arrange
        document_type = DocumentType.LICENSE_CERTIFICATE
        mock_session.exec.return_value.all.return_value = [mock_document]

        # Act
        result = document_service.get_documents_by_type(mock_session, document_type)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], DocumentResponse)
        assert result[0].id == mock_document.id

    def test_get_documents_by_type_empty(self, document_service, mock_session):
        # Arrange
        document_type = DocumentType.LICENSE_CERTIFICATE
        mock_session.exec.return_value.all.return_value = []

        # Act
        result = document_service.get_documents_by_type(mock_session, document_type)

        # Assert
        assert result == []

    def test_delete_document_success(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        current_user_id = mock_user.id
        mock_document.uploaded_by = mock_user.id  # Ensure user owns the document
        mock_session.get.return_value = mock_document
        mock_session.delete = Mock()
        mock_session.commit = Mock()
        document_service.storage.delete = Mock()

        # Act
        document_service.delete_document(mock_session, document_id, current_user_id)

        # Assert
        mock_session.get.assert_called_once_with(Document, document_id)
        document_service.storage.delete.assert_called_once_with(
            FileDeleteRequest(file_path=mock_document.file_path)
        )
        mock_session.delete.assert_called_once_with(mock_document)
        mock_session.commit.assert_called_once()

    def test_delete_document_not_found(self, document_service, mock_session, mock_user):
        # Arrange
        document_id = uuid4()
        current_user_id = mock_user.id
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            document_service.delete_document(mock_session, document_id, current_user_id)

        assert exc_info.value.status_code == 404
        assert "Document not found" in str(exc_info.value.message)

    def test_delete_document_forbidden(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        current_user_id = uuid4()  # Different user
        mock_session.get.return_value = mock_document

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            document_service.delete_document(mock_session, document_id, current_user_id)

        assert exc_info.value.status_code == 403
        assert "Not allowed" in str(exc_info.value.message)

    def test_delete_document_no_file_path(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        mock_document.file_path = None
        document_id = mock_document.id
        current_user_id = mock_user.id
        mock_document.uploaded_by = mock_user.id  # Ensure user owns the document
        mock_session.get.return_value = mock_document
        mock_session.delete = Mock()
        mock_session.commit = Mock()

        # Act
        document_service.delete_document(mock_session, document_id, current_user_id)

        # Assert
        document_service.storage.delete.assert_not_called()
        mock_session.delete.assert_called_once_with(mock_document)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_file_by_path(self, document_service):
        # Arrange
        file_path = "uploads/test/test.pdf"
        document_service.storage.delete = Mock()

        # Act
        await document_service.delete_file_by_path(file_path)

        # Assert
        document_service.storage.delete.assert_called_once_with(FileDeleteRequest(file_path=file_path))

    def test_get_document_file_success(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        mock_document.uploaded_by = mock_user.id  # Ensure user owns the document
        mock_session.get.return_value = mock_document
        mock_file = Mock()
        document_service.storage.open = Mock(return_value=mock_file)

        # Act
        result_file, result_doc = document_service.get_document_file(mock_session, document_id, mock_user)

        # Assert
        assert result_file == mock_file
        assert result_doc == mock_document
        document_service.storage.open.assert_called_once_with(
            FileReadRequest(file_path=mock_document.file_path)
        )

    def test_get_document_file_not_found(self, document_service, mock_session, mock_user):
        # Arrange
        document_id = uuid4()
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            document_service.get_document_file(mock_session, document_id, mock_user)

        assert exc_info.value.status_code == 404
        assert "Document not found" in str(exc_info.value.message)

    def test_get_document_file_forbidden_non_admin(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        mock_user.is_admin = False
        mock_document.uploaded_by = uuid4()  # Different user
        mock_session.get.return_value = mock_document

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            document_service.get_document_file(mock_session, document_id, mock_user)

        assert exc_info.value.status_code == 403
        assert "Not allowed to access this document" in str(exc_info.value.message)

    def test_get_document_file_admin_access(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        mock_user.is_admin = True
        mock_document.uploaded_by = uuid4()  # Different user
        mock_session.get.return_value = mock_document
        mock_file = Mock()
        document_service.storage.open = Mock(return_value=mock_file)

        # Act
        result_file, result_doc = document_service.get_document_file(mock_session, document_id, mock_user)

        # Assert
        assert result_file == mock_file
        assert result_doc == mock_document

    def test_get_document_file_no_file_path(self, document_service, mock_session, mock_document, mock_user):
        # Arrange
        document_id = mock_document.id
        mock_document.file_path = None
        mock_document.uploaded_by = mock_user.id  # Ensure user owns the document
        mock_session.get.return_value = mock_document

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            document_service.get_document_file(mock_session, document_id, mock_user)

        assert exc_info.value.status_code == 404
        assert "File not found" in str(exc_info.value.message)