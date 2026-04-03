import sys
from pathlib import Path

# Add the project root to sys.path so src/ can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlmodel import SQLModel, create_engine, Session
from uuid import uuid4

# Import all models to ensure tables are created
from src.auth.models import User, UserAuth, UserRole, UserStatus
from src.profiles.models import (
    LicenseHolderProfile,
    EquipmentOwnerProfile,
    ConsultantProfile,
    BuyerProfile,
)
from src.requests.models import (
    Request,
    ConsultingRequest,
    MineralSellerRequest,
    LicenseSellRequest,
    MineralBuyerRequest,
)

# Test database setup
engine = create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before tests and drop after."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def session():
    """Provide a database session for each test."""
    with Session(engine) as session:
        yield session


# Sample data fixtures
@pytest.fixture
def sample_user(session):
    """Create a sample approved user."""
    unique_id = str(uuid4())[:8]
    user = User(
        full_name="John Doe",
        email=f"john{unique_id}@example.com",
        phone="1234567890",
        role=UserRole.BUYER,
        status=UserStatus.APPROVED,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def sample_license_holder_user(session):
    """Create a sample approved license holder user."""
    unique_id = str(uuid4())[:8]
    user = User(
        full_name="John Doe",
        email=f"john{unique_id}@example.com",
        phone="1234567890",
        role=UserRole.LICENSE_HOLDER,
        status=UserStatus.APPROVED,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_user_auth(session, sample_user):
    """Create auth record for sample user."""
    from src.auth.services import _create_user_auth_record
    _create_user_auth_record("password123", sample_user.id, session)
    return sample_user


@pytest.fixture
def sample_staff_user(session):
    """Create a sample staff user."""
    unique_id = str(uuid4())[:8]
    user = User(
        full_name="Staff User",
        email=f"staff{unique_id}@example.com",
        phone="0987654321",
        role=UserRole.STAFF,
        status=UserStatus.APPROVED,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_pending_user(session):
    """Create a sample pending user."""
    unique_id = str(uuid4())[:8]
    user = User(
        full_name="Pending User",
        email=f"pending{unique_id}@example.com",
        phone="1111111111",
        role=UserRole.CONSULTANT,
        status=UserStatus.PENDING,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_request(session, sample_user):
    """Create a sample request."""
    request = Request(
        requester_id=sample_user.id,
        request_type="OTHER",
        more_detail="Test request",
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return request