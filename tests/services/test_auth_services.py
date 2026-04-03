import pytest
from uuid import uuid4
from sqlmodel import select

from src.auth.services import (
    get_user_by_id,
    login_service,
    registration_service,
    update_user,
)
from src.auth.models import User, UserAuth, UserRole, UserStatus
from src.auth.schemas import (
    LoginRequest,
    RegisterUserRequest,
    UserUpdate,
)
from src.auth.exceptions import (
    UserNotFoundError,
    LoginError,
    EmailExistsError,
)
from src.profiles.exceptions import NotAllowed


class TestGetUserById:
    def test_get_user_by_id_success(self, session, sample_user):
        """Test successful user retrieval."""
        result = get_user_by_id(sample_user.id, session)
        assert result.id == sample_user.id
        assert result.email == sample_user.email

    def test_get_user_by_id_not_found(self, session):
        """Test user not found raises exception."""
        with pytest.raises(UserNotFoundError):
            get_user_by_id(uuid4(), session)


class TestLoginService:
    def test_login_service_success(self, session, sample_user_auth):
        """Test successful login."""
        login_data = LoginRequest(email=sample_user_auth.email, password="password123")
        result = login_service(login_data, session)
        assert result.id == sample_user_auth.id
        assert result.status == UserStatus.APPROVED

    def test_login_service_user_not_found(self, session):
        """Test login with non-existent user."""
        login_data = LoginRequest(email="nonexistent@example.com", password="password")
        with pytest.raises(LoginError):
            login_service(login_data, session)

    def test_login_service_no_auth_record(self, session, sample_user):
        """Test login when user has no auth record."""
        # Remove auth record
        stmt = select(UserAuth).where(UserAuth.user_id == sample_user.id)
        auth_record = session.exec(stmt).first()
        if auth_record:
            session.delete(auth_record)
            session.commit()

        login_data = LoginRequest(email=sample_user.email, password="password")
        with pytest.raises(LoginError):
            login_service(login_data, session)

    def test_login_service_wrong_password(self, session, sample_user_auth):
        """Test login with wrong password."""
        login_data = LoginRequest(email="john@example.com", password="wrongpassword")
        with pytest.raises(LoginError):
            login_service(login_data, session)

    def test_login_service_unapproved_user(self, session, sample_pending_user):
        """Test login with unapproved user."""
        # Create auth for pending user
        from src.auth.services import _create_user_auth_record
        _create_user_auth_record("password123", sample_pending_user.id, session)

        login_data = LoginRequest(email=sample_pending_user.email, password="password123")
        with pytest.raises(Exception):  # Should raise UnApprovedUserErrorLogin
            login_service(login_data, session)


class TestRegistrationService:
    def test_registration_service_success(self, session):
        """Test successful user registration."""
        reg_data = RegisterUserRequest(
            full_name="Jane Doe",
            email="jane@example.com",
            phone="9876543210",
            role=UserRole.CONSULTANT,
            password="password123",
        )
        result = registration_service(reg_data, session)
        assert result.full_name == "Jane Doe"
        assert result.email == "jane@example.com"
        assert result.status == UserStatus.PENDING

        # Check auth record created
        auth_record = session.exec(
            select(UserAuth).where(UserAuth.user_id == result.id)
        ).first()
        assert auth_record is not None

    def test_registration_service_email_exists(self, session, sample_user):
        """Test registration with existing email."""
        reg_data = RegisterUserRequest(
            full_name="Another User",
            email=sample_user.email,  # Existing email
            phone="1111111111",
            role=UserRole.BUYER,
            password="password123",
        )
        with pytest.raises(EmailExistsError):
            registration_service(reg_data, session)


class TestUpdateUser:
    def test_update_user_success_self(self, session, sample_user):
        """Test user updating their own info."""
        update_data = UserUpdate(full_name="John Updated", phone="9999999999")
        result = update_user(sample_user, sample_user.id, update_data, session)
        assert result.full_name == "John Updated"
        assert result.phone == "9999999999"

    def test_update_user_success_staff(self, session, sample_staff_user, sample_user):
        """Test staff updating user info."""
        update_data = UserUpdate(full_name="Updated by Staff")
        result = update_user(sample_staff_user, sample_user.id, update_data, session)
        assert result.full_name == "Updated by Staff"

    def test_update_user_not_allowed(self, session, sample_user, sample_pending_user):
        """Test non-staff user trying to update another user."""
        update_data = UserUpdate(full_name="Should Fail")
        with pytest.raises(NotAllowed):
            update_user(sample_user, sample_pending_user.id, update_data, session)

    def test_update_user_email_conflict(self, session, sample_user, sample_pending_user):
        """Test updating to existing email."""
        update_data = UserUpdate(email=sample_pending_user.email)  # Existing email
        with pytest.raises(EmailExistsError):
            update_user(sample_user, sample_user.id, update_data, session)

    def test_update_user_not_found(self, session, sample_user):
        """Test updating non-existent user."""
        update_data = UserUpdate(full_name="Test")
        with pytest.raises(UserNotFoundError):
            update_user(sample_user, uuid4(), update_data, session)