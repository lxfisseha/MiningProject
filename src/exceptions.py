from fastapi.exceptions import HTTPException


class BaseException(HTTPException):
    def __init__(self, status_code: int, message: str, *args):
        super().__init__(status_code, message, *args)
        self.message = message


class PermisionError(BaseException):
    def __init__(self, status_code: int = 401, message="permision denied.", *args):
        super().__init__(status_code, message, *args)
