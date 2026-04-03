import pytest
from uuid import uuid4

from src.profiles.services import (
    get_profile_model,
    get_profile_response_model,
    get_profile_data_attribute_name,
    create_user_profile,
    update_profile,
    get_profile_by_user,
    get_user_with_profile,
)
from src.profiles.models import LicenseType
from src.profiles.schemas import (
    ProfileRegistrationRequest,
    BuyerCreate,
    ProfileUpdateRequest,
    BuyerProfileUpdate,
)
from src.profiles.exceptions import (
    InvalidRoleError,
    UserAlreadyHasProfileError,
    ProfileInfoMissingError,
    IncompleteRegistrationProfileNotFoundError,
    NotAllowed,
)
from src.auth.exceptions import UserNotFoundError
from src.auth.models import UserRole, UserStatus

class TestGetProfileModel:
    def test_get_profile_model_license_holder(self):
        """Test getting profile model for license holder."""
        result = get_profile_model(UserRole.LICENSE_HOLDER)
        assert result.__name__ == "LicenseHolderProfile"

    def test_get_profile_model_buyer(self):
        """Test getting profile model for buyer."""
        result = get_profile_model(UserRole.BUYER)
        assert result.__name__ == "BuyerProfile"

    def test_get_profile_model_invalid_role(self):
        """Test invalid role raises exception."""
        with pytest.raises(InvalidRoleError):
            get_profile_model("INVALID_ROLE")


class TestGetProfileResponseModel:
    def test_get_profile_response_model_success(self):
        """Test getting response model."""
        result = get_profile_response_model(UserRole.BUYER)
        assert result.__name__ == "BuyerProfileResponse"

    def test_get_profile_response_model_invalid_role(self):
        """Test invalid role raises exception."""
        with pytest.raises(InvalidRoleError):
            get_profile_response_model("INVALID")


class TestGetProfileDataAttributeName:
    def test_get_profile_data_attribute_name_success(self):
        """Test getting attribute name."""
        result = get_profile_data_attribute_name(UserRole.CONSULTANT)
        assert result == "consultant_profile"

    def test_get_profile_data_attribute_name_invalid_role(self):
        """Test invalid role raises exception."""
        with pytest.raises(InvalidRoleError):
            get_profile_data_attribute_name("INVALID")


class TestCreateUserProfile:
    def test_create_user_profile_success(self, session, sample_user):
        """Test successful profile creation."""
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        result = create_user_profile(reg_request, session, sample_user.id)
        assert result.user_id == sample_user.id
        assert result.industry_type == "Mining"

    def test_create_user_profile_already_has_profile(self, session, sample_user):
        """Test creating profile when user already has one."""
        # Create profile first
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        create_user_profile(reg_request, session, sample_user.id)

        # Try to create again
        with pytest.raises(UserAlreadyHasProfileError):
            create_user_profile(reg_request, session, sample_user.id)

    def test_create_user_profile_missing_data(self, session, sample_user):
        """Test creating profile with missing data."""
        reg_request = ProfileRegistrationRequest()  # No profile data
        with pytest.raises(ProfileInfoMissingError):
            create_user_profile(reg_request, session, sample_user.id)

    def test_create_user_profile_invalid_user(self, session):
        """Test creating profile for non-existent user."""
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        with pytest.raises(UserNotFoundError):
            create_user_profile(reg_request, session, uuid4())


class TestUpdateProfile:
    def test_update_profile_success_self(self, session, sample_user):
        """Test user updating their own profile."""
        # Create profile first
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        create_user_profile(reg_request, session, sample_user.id)

        # Update
        update_data = BuyerProfileUpdate(industry_type="Updated Mining")
        update_request = ProfileUpdateRequest(buyer_profile=update_data)
        result = update_profile(sample_user, sample_user.id, update_request, session)
        assert result.industry_type == "Updated Mining"

    def test_update_profile_not_allowed(self, session, sample_user, sample_pending_user):
        """Test non-owner updating profile."""
        with pytest.raises(NotAllowed):
            update_data = BuyerProfileUpdate(industry_type="Test")
            update_request = ProfileUpdateRequest(buyer_profile=update_data)
            update_profile(sample_user, sample_pending_user.id, update_request, session)

    def test_update_profile_no_profile(self, session, sample_user):
        """Test updating when no profile exists."""
        update_data = BuyerProfileUpdate(industry_type="Test")
        update_request = ProfileUpdateRequest(buyer_profile=update_data)
        with pytest.raises(IncompleteRegistrationProfileNotFoundError):
            update_profile(sample_user, sample_user.id, update_request, session)


class TestGetProfileByUser:
    def test_get_profile_by_user_success(self, session, sample_user):
        """Test getting profile by user."""
        # Create profile
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        create_user_profile(reg_request, session, sample_user.id)

        result = get_profile_by_user(sample_user, session)
        assert result.user_id == sample_user.id

    def test_get_profile_by_user_no_profile(self, session, sample_user):
        """Test getting profile when none exists."""
        with pytest.raises(IncompleteRegistrationProfileNotFoundError):
            get_profile_by_user(sample_user, session)


class TestGetUserWithProfile:
    def test_get_user_with_profile_success(self, session, sample_user):
        """Test getting user with profile."""
        # Create profile
        profile_data = BuyerCreate(
            industry_type="Mining",
            plant_location="Location A",
        )
        reg_request = ProfileRegistrationRequest(buyer_profile=profile_data)
        create_user_profile(reg_request, session, sample_user.id)

        result = get_user_with_profile(sample_user, session)
        assert result.id == sample_user.id
        assert result.buyer_profile is not None
        assert result.buyer_profile.industry_type == "Mining"

    def test_get_user_with_profile_no_profile(self, session, sample_user):
        """Test getting user with profile when none exists."""
        with pytest.raises(IncompleteRegistrationProfileNotFoundError):
            get_user_with_profile(sample_user, session)