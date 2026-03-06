from src.exceptions import BaseException


class ProfileInfoMissingError(BaseException):
    def __init__(
        self, status_code: int = 404, message="profile information is missing", *args
    ):
        super().__init__(status_code, message, *args)


class UserAlreadyHasProfileError(BaseException):
    def __init__(
        self, status_code=401, message="user with given id already has a profile", *args
    ):
        super().__init__(status_code, message, *args)


class ProfileRoleMissmatch(BaseException):
    def __init__(
        self, status_code=401, message="user profile and role dont match", *args
    ):
        super().__init__(status_code, message, *args)
