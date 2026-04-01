from uuid import UUID

from sqlalchemy import Select

from src.auth import models as auth_models
from src.auth import services as auth_services
from sqlmodel import desc, or_, select, func, case, Session

from src.staff.schemas import UserFilters, UserSortOptions

from .exceptions import PermissionDeniedError


def change_user_status(
    actor: auth_models.User,
    session: Session,
    user_id: UUID,
    status: auth_models.UserStatus,
):
    if not actor.is_staff_or_admin:
        raise PermissionDeniedError()

    user = auth_services.get_user_by_id(user_id, session)
    user.status = status
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_pending_users(actor: auth_models.User, session: Session, filters: UserFilters):
    if not actor.is_staff_or_admin:
        raise PermissionDeniedError()
    filters.status = auth_models.UserStatus.PENDING
    filters.limit = 100

    users = get_users(actor, session, filters)
    return users


def get_users(actor: auth_models.User, session: Session, filters: UserFilters):
    if not actor.is_staff_or_admin:
        raise PermissionDeniedError()

    statement = select(auth_models.User)
    if filters.search != "":
        statement = _search_user_select_statement(statement, filters.search)
    if filters.status is not None:
        statement = statement.where(auth_models.User.status == filters.status)
    if filters.role is not None:
        statement = statement.where(auth_models.User.role == filters.role)
    statement = _sort_user_select_statement(filters.sorting, statement)
    
    statement = statement.offset(filters.offset).limit(filters.limit)

    return session.exec(statement).all()


def _search_user_select_statement(statement: Select, s: str = ""):
    statement = statement.where(
        or_(
            auth_models.User.email.ilike(f"%{s}%"),
            auth_models.User.full_name.ilike(f"%{s}%"),
        )
    )
    return statement


def _sort_user_select_statement(sort_option: UserSortOptions, statement: Select):
    if sort_option == UserSortOptions.oldest_first:
        statement = statement.order_by(auth_models.User.created_at)
    else:
        statement = statement.order_by(desc(auth_models.User.created_at))

    return statement


def get_new_requests():
    pass


def get_all_requests_by_user():
    pass
