from src.exceptions import BaseException


class AuthenticationErrorBase(BaseException):
    pass


class CredentialsError(AuthenticationErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "could not validate credentials",
        *args,
    ):
        super().__init__(status_code, message, *args)


class EmailExistsError(BaseException):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "email is already in use.",
        *args,
    ):
        super().__init__(status_code, message, *args)


class UserNotFoundError(BaseException):
    def __init__(
        self,
        status_code: int = 404,
        message: str = "user not found",
        *args,
    ):
        super().__init__(message, *args)
