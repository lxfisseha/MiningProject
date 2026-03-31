from src.exceptions import BaseException


class RequestErrorBase(BaseException):
    pass


class StaffNotAllowed(RequestErrorBase):
    def __init__(self, status_code: int = 401, message="staff not allowed.", *args):
        super().__init__(status_code, message, *args)


class RequestNotFoundError(RequestErrorBase):
    def __init__(self, status_code: int = 401, message="request not found.", *args):
        super().__init__(status_code, message, *args)


class RequestNotAllowed(RequestErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message="you are not allowed to access this request.",
        *args
    ):
        super().__init__(status_code, message, *args)


class RequestTypeNotAllowed(RequestErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message="you are not allowed to create this request type.",
        *args
    ):
        super().__init__(status_code, message, *args)


class RequestInfoNotFound(RequestErrorBase):
    def __init__(
        self, status_code: int = 401, message="request info not found.", *args
    ):
        super().__init__(status_code, message, *args)


class InvalidRequestType(RequestErrorBase):
    def __init__(self, status_code: int = 401, message="invalid request types.", *args):
        super().__init__(status_code, message, *args)


class RequestCanNotBeUpdated(RequestErrorBase):
    def __init__(
        self, status_code: int = 401, message="request can not be updated.", *args
    ):
        super().__init__(status_code, message, *args)
