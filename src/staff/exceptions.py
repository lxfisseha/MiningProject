from src.exceptions import BaseException


class PermissionDeniedError(BaseException):
    def __init__(
        self, status_code: int = 401, message="only staff and admin are allowed.", *args
    ):
        super().__init__(status_code, message, *args)
