from src.exceptions import BaseException
from src.auth.exceptions import RegistrationErrorBase

class ProfileRegistrationError(RegistrationErrorBase):
    pass

class ProfileInfoMissingError(ProfileRegistrationError):
    def __init__(
        self, status_code: int = 404, message="profile information is missing", *args
    ):
        super().__init__(status_code, message, *args)


class UserAlreadyHasProfileError(ProfileRegistrationError):
    def __init__(
        self, status_code=401, message="user with given id already has a profile", *args
    ):
        super().__init__(status_code, message, *args)


class InvalidRoleError(ProfileRegistrationError):
    def __init__(self, status_code=401, message="Invalid role", *args):
        super().__init__(status_code, message, *args)

class ProfileEditError(BaseException):
    pass

class NotAllowed(ProfileEditError):
    def __init__(self, status_code=401, message="not allowed to edit profile", *args):
        super().__init__(status_code, message, *args)

class IncompleteRegistrationProfileNotFoundError(BaseException):
    def __init__(self, status_code=401, message="profile not found",user_id=None, *args):
        super().__init__(status_code, message, *args)
        self.user_id = user_id
