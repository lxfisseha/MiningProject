from src.exceptions import BaseException

class DocumentException(BaseException):
    pass

class MissingDocumentsError(DocumentException):
    def __init__(self):
        self.message = "No Documents provided for upload!"
        self.status_code = 400

class MissingRequiredDocumentError(DocumentException):
    def __init__(self, document_name: str):
        self.message = f"Required document '{document_name}' is missing"
        self.status_code = 400

class UnexpectedDocumentError(DocumentException):
    def __init__(self, unexpected_fields: set):
        self.message = f"Unexpected document fields: {unexpected_fields}"
        self.status_code = 400

class UnableToSaveDocumentError(DocumentException):
    def __init__(self, details: str):
        self.message = f"Unable to save document: {details}"
        self.status_code = 500

class UnableToCreateDocumentRecordError(DocumentException):
    def __init__(self, details: str):
        self.message = f"Unable to create document record: {details}"
        self.status_code = 500

class InvalidprofileFieldError(DocumentException):
    def __init__(self, field_name: str):
        self.message = f"Invalid profile field {field_name}"
        self.status_code = 400

class InvalidFileTypeError(DocumentException):
    def __init__(self, content_type: str):
        self.message = f"Unsupported file type: {content_type}"
        self.status_code = 400

class FileHasNoNameError(DocumentException):
    def __init__(self):
        self.message = "File must have a name"
        self.status_code = 400