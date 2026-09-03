from sqlmodel import Session, select

from .database import engine
from .auth.models import User, UserAuth, UserRole, UserStatus
from .auth.utils import hash_password


DEMO_USERS = [
    {"full_name": "Admin User", "email": "admin@gmail.com", "phone": "0000000000", "role": UserRole.ADMIN},
    {"full_name": "Staff User", "email": "staff@gmail.com", "phone": "0000000001", "role": UserRole.STAFF},
    {"full_name": "Buyer User", "email": "buyer@gmail.com", "phone": "0000000002", "role": UserRole.BUYER},
    {"full_name": "Consultant User", "email": "consultant@gmail.com", "phone": "0000000003", "role": UserRole.CONSULTANT},
    {"full_name": "License Holder", "email": "licenseholder@gmail.com", "phone": "0000000004", "role": UserRole.LICENSE_HOLDER},
    {"full_name": "Equipment Owner", "email": "equipmentowner@gmail.com", "phone": "0000000005", "role": UserRole.EQUIPMENT_OWNER},
]

DEFAULT_PASSWORD = "password"


def seed_demo_users():
    with Session(engine) as session:
        for user_data in DEMO_USERS:
            existing = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()
            if existing:
                continue
            user = User(**user_data, status=UserStatus.APPROVED)
            session.add(user)
            session.flush()
            auth = UserAuth(user_id=user.id, hashed_password=hash_password(DEFAULT_PASSWORD))
            session.add(auth)
        session.commit()
