from multiprocessing.context import AuthenticationError

from src.exceptions import BaseException


class AuthenticationErrorBase(BaseException):
    pass

class LoginRequiredError(AuthenticationError):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "login required.",
        *args,
    ):
        super().__init__(status_code, message, *args)


class CredentialsError(AuthenticationErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "could not validate credentials",
        *args,
    ):
        super().__init__(status_code, message, *args)

class LoginError(AuthenticationErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "invalid username or password",
        *args,
    ):
        super().__init__(status_code, message, *args)

class UnApprovedUserErrorLogin(LoginError):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "User is not yet approved",
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
        super().__init__(status_code, message, *args)

class RegistrationErrorBase(BaseException):
    def __init__(
        self,
        status_code: int = 422,
        message: str = "registration failed please try again",
        *args,
    ):
        super().__init__(status_code, message, *args)

class EmailExistsError(RegistrationErrorBase):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "email is already in use.",
        *args,
    ):
        super().__init__(status_code, message, *args)

class EditProfileError(BaseException):
    pass

class NotAllowedError(EditProfileError):
    def __init__(
        self,
        status_code: int = 402,
        message: str = "you are not allowed to perform this action.",
        *args,
    ):
        super().__init__(status_code, message, *args)

class WrongPasswordError(EditProfileError):
    def __init__(
        self,
        status_code: int = 401,
        message: str = "wrong password provided.",
        *args,
    ):
        super().__init__(status_code, message, *args)


class FailedToCreateAuthRecord(RegistrationErrorBase):
    pass

class ProfileCreationFailedError(RegistrationErrorBase):
    pass