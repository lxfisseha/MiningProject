import pytest
from uuid import uuid4

from src.staff.services import (
    change_user_status,
    get_pending_users,
    get_users,
    get_total_users_count,
    get_all_requests,
    get_total_requests_count,
)
from src.staff.schemas import UserFilters, RequestsFilters, UserSortOptions
from src.auth.models import UserStatus, UserRole
from src.staff.exceptions import PermissionDeniedError


class TestChangeUserStatus:
    def test_change_user_status_success(self, session, sample_staff_user, sample_pending_user):
        """Test staff changing user status."""
        result = change_user_status(sample_staff_user, session, sample_pending_user.id, UserStatus.APPROVED)
        assert result.status == UserStatus.APPROVED

    def test_change_user_status_not_staff(self, session, sample_user, sample_pending_user):
        """Test non-staff cannot change status."""
        with pytest.raises(PermissionDeniedError):
            change_user_status(sample_user, session, sample_pending_user.id, UserStatus.APPROVED)

    def test_change_user_status_user_not_found(self, session, sample_staff_user):
        """Test changing status of non-existent user."""
        with pytest.raises(Exception):  # UserNotFoundError from auth service
            change_user_status(sample_staff_user, session, uuid4(), UserStatus.APPROVED)


class TestGetPendingUsers:
    def test_get_pending_users_success(self, session, sample_staff_user, sample_pending_user):
        """Test getting pending users."""
        filters = UserFilters()
        result = get_pending_users(sample_staff_user, session, filters)
        assert len(result) >= 1
        assert all(user.status == UserStatus.PENDING for user in result)

    def test_get_pending_users_not_staff(self, session, sample_user):
        """Test non-staff cannot get pending users."""
        filters = UserFilters()
        with pytest.raises(PermissionDeniedError):
            get_pending_users(sample_user, session, filters)


class TestGetUsers:
    def test_get_users_success(self, session, sample_staff_user):
        """Test getting users."""
        filters = UserFilters()
        result = get_users(sample_staff_user, session, filters)
        assert isinstance(result, list)

    def test_get_users_not_staff(self, session, sample_user):
        """Test non-staff cannot get users."""
        filters = UserFilters()
        with pytest.raises(PermissionDeniedError):
            get_users(sample_user, session, filters)

    def test_get_users_with_filters(self, session, sample_staff_user, sample_user):
        """Test getting users with filters."""
        filters = UserFilters(status=UserStatus.APPROVED, role=UserRole.BUYER)
        result = get_users(sample_staff_user, session, filters)
        assert all(user.status == UserStatus.APPROVED and user.role == UserRole.BUYER for user in result)


class TestGetTotalUsersCount:
    def test_get_total_users_count_success(self, session, sample_staff_user):
        """Test getting total users count."""
        filters = UserFilters()
        result = get_total_users_count(sample_staff_user, session, filters)
        assert isinstance(result, int)
        assert result >= 1

    def test_get_total_users_count_not_staff(self, session, sample_user):
        """Test non-staff cannot get count."""
        filters = UserFilters()
        with pytest.raises(PermissionDeniedError):
            get_total_users_count(sample_user, session, filters)


class TestGetAllRequests:
    def test_get_all_requests_success(self, session, sample_staff_user, sample_request):
        """Test getting all requests."""
        filters = RequestsFilters()
        result = get_all_requests(sample_staff_user, session, filters)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_all_requests_not_staff(self, session, sample_user):
        """Test non-staff cannot get all requests."""
        filters = RequestsFilters()
        with pytest.raises(PermissionDeniedError):
            get_all_requests(sample_user, session, filters)


class TestGetTotalRequestsCount:
    def test_get_total_requests_count_success(self, session, sample_staff_user):
        """Test getting total requests count."""
        filters = RequestsFilters()
        result = get_total_requests_count(sample_staff_user, session, filters)
        assert isinstance(result, int)

    def test_get_total_requests_count_not_staff(self, session, sample_user):
        """Test non-staff cannot get count."""
        filters = RequestsFilters()
        with pytest.raises(PermissionDeniedError):
            get_total_requests_count(sample_user, session, filters)