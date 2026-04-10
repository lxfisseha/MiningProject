from src.exceptions import BaseException

class DocumentException(BaseException):
    pass

class MissingDocumentsError(DocumentException):
    def __init__(self):
        self.message = "No Documents provided for upload!"

class MissingRequiredDocumentError(DocumentException):
    def __init__(self, document_name: str):
        self.message = f"Required document '{document_name}' is missing"

class UnexpectedDocumentError(DocumentException):
    def __init__(self, unexpected_fields: set):
        self.message = f"Unexpected document fields: {unexpected_fields}"

class UnableToSaveDocumentError(DocumentException):
    def __init__(self, details: str):
        self.message = f"Unable to save document: {details}"

class UnableToCreateDocumentRecordError(DocumentException):
    def __init__(self, details: str):
        self.message = f"Unable to create document record: {details}"

class InvalidprofileFieldError(DocumentException):
    def __init__(self, field_name: str):
        self.message = f"Invalid profile field {field_name}"

class InvalidFileTypeError(DocumentException):
    def __init__(self, content_type: str):
        self.message = f"Unsupported file type: {content_type}"

class FileHasNoNameError(DocumentException):
    def __init__(self):
        self.message = "File must have a name"