import pytest
from uuid import uuid4

from src.requests.services import (
    create_request,
    update_request,
    get_my_requests,
    get_user_request_stats,
    get_request_with_detail,
    get_request_id,
    get_request_detail,
)
from src.requests.schemas import (
    RequestCreate,
    RequestUpdate,
    RequestFilters,
    ConsultingRequestCreate,
    RequestSortOptions,
)
from src.staff.schemas import RequestsFilters
from src.requests.models import Request
from src.requests.enums import RequestType, RequestStatus
from src.requests.enums import ConsultancyType, StudyLevel
from src.requests.exceptions import (
    RequestTypeNotAllowed,
    RequestInfoNotFound,
    RequestNotFoundError,
    RequestNotAllowed,
    RequestCanNotBeUpdated,
)
from src.auth.models import UserRole
from src.staff.services import get_all_requests, get_total_requests_count


class TestCreateRequest:
    def test_create_request_other_success(self, session, sample_user):
        """Test creating OTHER request."""
        request_data = RequestCreate(
            request_type=RequestType.OTHER,
            more_detail="Test other request",
        )
        result = create_request(session, request_data, sample_user)
        assert result.request_type == RequestType.OTHER
        assert result.more_detail == "Test other request"
        assert result.requester_id == sample_user.id

    def test_create_request_consulting_success(self, session, sample_license_holder_user):
        """Test creating CONSULTING request."""
        consulting_data = ConsultingRequestCreate(
            consultancy_type=ConsultancyType.EXPLORATION,
            expert_type="Geologist",
            drill_machine_required=True,
            study_level=StudyLevel.EXPLORATION,
            location="Test Location",
            license_holder_name="Test Holder",
            license_number="12345",
            material_type="Gold",
        )
        request_data = RequestCreate(
            request_type=RequestType.CONSULTING,
            more_detail="Consulting request",
            consulting_request=consulting_data,
        )
        result = create_request(session, request_data, sample_license_holder_user)
        assert result.request_type == RequestType.CONSULTING
        assert result.consulting_request is not None
        assert result.consulting_request.expert_type == "Geologist"

    def test_create_request_type_not_allowed(self, session, sample_user):
        """Test creating request type not allowed for role."""
        # BUYER cannot create CONSULTING
        consulting_data = ConsultingRequestCreate(
            consultancy_type=ConsultancyType.EXPLORATION,
            expert_type="Geologist",
            drill_machine_required=False,
            study_level=StudyLevel.EXPLORATION,
            location="Test",
            license_holder_name="Test",
            license_number="123",
            material_type="Test",
        )
        request_data = RequestCreate(
            request_type=RequestType.CONSULTING,
            consulting_request=consulting_data,
        )
        with pytest.raises(RequestTypeNotAllowed):
            create_request(session, request_data, sample_user)

    def test_create_request_missing_detail(self, session, sample_license_holder_user):
        """Test creating request with missing detail data."""
        request_data = RequestCreate(
            request_type=RequestType.CONSULTING,
            # No consulting_request data
        )
        with pytest.raises(RequestInfoNotFound):
            create_request(session, request_data, sample_license_holder_user)


class TestUpdateRequest:
    def test_update_request_success(self, session, sample_user, sample_request):
        """Test updating request."""
        update_data = RequestUpdate(more_detail="Updated detail")
        result = update_request(session, sample_request.id, update_data, sample_user)
        assert result.more_detail == "Updated detail"

    def test_update_request_not_allowed(self, session, sample_user, sample_request, sample_pending_user):
        """Test updating request by non-owner."""
        update_data = RequestUpdate(more_detail="Test")
        with pytest.raises(RequestNotAllowed):
            update_request(session, sample_request.id, update_data, sample_pending_user)

    def test_update_request_not_found(self, session, sample_user):
        """Test updating non-existent request."""
        update_data = RequestUpdate(more_detail="Test")
        with pytest.raises(RequestNotFoundError):
            update_request(session, uuid4(), update_data, sample_user)

    def test_update_request_cannot_update(self, session, sample_user, sample_request):
        """Test updating request that cannot be updated."""
        # Change status to COMPLETED
        sample_request.status = RequestStatus.COMPLETED
        session.add(sample_request)
        session.commit()

        update_data = RequestUpdate(more_detail="Test")
        with pytest.raises(RequestCanNotBeUpdated):
            update_request(session, sample_request.id, update_data, sample_user)


class TestGetMyRequests:
    def test_get_my_requests_success(self, session, sample_user, sample_request):
        """Test getting user's requests."""
        filters = RequestFilters(limit=10, offset=0)
        result = get_my_requests(session, sample_user, filters)
        assert len(result) == 1
        assert result[0].id == sample_request.id

    def test_get_my_requests_staff_not_allowed(self, session, sample_staff_user):
        """Test staff cannot get my requests."""
        filters = RequestFilters()
        with pytest.raises(Exception):  # StaffNotAllowed
            get_my_requests(session, sample_staff_user, filters)

    def test_get_my_requests_with_filters(self, session, sample_user, sample_request):
        """Test getting requests with filters."""
        filters = RequestFilters(request_type=RequestType.OTHER)
        result = get_my_requests(session, sample_user, filters)
        assert len(result) == 1

        filters = RequestFilters(request_type=RequestType.CONSULTING)
        result = get_my_requests(session, sample_user, filters)
        assert len(result) == 0


class TestGetUserRequestStats:
    def test_get_user_request_stats_success(self, session, sample_user, sample_request):
        """Test getting user stats."""
        result = get_user_request_stats(sample_user, sample_user.id, session)
        assert result.user_id == sample_user.id
        assert result.total_requests == 1
        assert result.pending_requests == 1  # NEW status

    def test_get_user_request_stats_not_allowed(self, session, sample_user, sample_pending_user):
        """Test getting stats for another user."""
        with pytest.raises(RequestNotAllowed):
            get_user_request_stats(sample_user, sample_pending_user.id, session)


class TestGetRequestWithDetail:
    def test_get_request_with_detail_success(self, session, sample_user, sample_request):
        """Test getting request with detail."""
        result = get_request_with_detail(session, sample_request.id, sample_user)
        assert result.id == sample_request.id

    def test_get_request_with_detail_not_allowed(self, session, sample_request, sample_pending_user):
        """Test getting request by non-owner."""
        with pytest.raises(RequestNotAllowed):
            get_request_with_detail(session, sample_request.id, sample_pending_user)