from uuid import UUID

from sqlalchemy import Select, case, desc
from sqlmodel import Session, select, case, func

from src.auth import models as auth_models
from .enums import RequestSortOptions, RequestStatus, RequestType
from .exceptions import (
    StaffNotAllowed,
    RequestNotFoundError,
    RequestNotAllowed,
    InvalidRequestType,
    RequestInfoNotFound,
    RequestTypeNotAllowed,
    RequestCanNotBeUpdated,
)
from .schemas import (
    RequestFilters,
    RequestDetailResponse,
    RequestCreate,
    ConsultingRequestResponse,
    LicenseSellRequestResponse,
    MineralBuyerRequestResponse,
    MineralSellerRequestResponse,
    RequestUpdate,
    RequestResponse,
    UserStatsResponse,
)
from .models import (
    Request,
    MineralSellerRequest,
    ConsultingRequest,
    LicenseSellRequest,
    MineralBuyerRequest,
)
from . import config

request_type_to_request_detail_attribute_name = {
    RequestType.CONSULTING: "consulting_request",
    RequestType.LICENSE_SELL: "license_sell_request",
    RequestType.MINERAL_BUYER: "mineral_buy_request",
    RequestType.MINERAL_SELLER: "mineral_sell_request",
}

request_type_to_model_map = {
    RequestType.CONSULTING: ConsultingRequest,
    RequestType.LICENSE_SELL: LicenseSellRequest,
    RequestType.MINERAL_BUYER: MineralBuyerRequest,
    RequestType.MINERAL_SELLER: MineralSellerRequest,
}

request_type_to_response_model_map = {
    RequestType.CONSULTING: ConsultingRequestResponse,
    RequestType.LICENSE_SELL: LicenseSellRequestResponse,
    RequestType.MINERAL_BUYER: MineralBuyerRequestResponse,
    RequestType.MINERAL_SELLER: MineralSellerRequestResponse,
}


def _get_request_detail_attribute_name(request_type: RequestType) -> str:
    attr = request_type_to_request_detail_attribute_name.get(request_type, None)
    if not attr:
        raise InvalidRequestType()
    return attr


def _get_request_detail_model(request_type: RequestType) -> type:
    model = request_type_to_model_map.get(request_type, None)
    if not model:
        raise InvalidRequestType()
    return model


def _get_request_detail_response_model(request_type: RequestType) -> type:
    model = request_type_to_response_model_map.get(request_type, None)
    if not model:
        raise InvalidRequestType()
    return model


def create_request(
    session: Session, data: RequestCreate, actor: auth_models.User
) -> RequestDetailResponse:
    if data.request_type not in config.ALLOWED_REQUEST_TYPES_TO_ROLES[actor.role]:
        raise RequestTypeNotAllowed()

    request = Request(
        requester_id=actor.id,
        request_type=data.request_type,
        more_detail=data.more_detail,
    )

    session.add(request)
    session.flush()

    if request.request_type == RequestType.OTHER:
        session.commit()
        return RequestDetailResponse.model_validate(request)

    request_detail_model = _get_request_detail_model(data.request_type)
    request_data_attr_name = _get_request_detail_attribute_name(data.request_type)

    print("we found the request detail model:", request_detail_model)
    print("we found the request attribute model:", request_data_attr_name)
    detail_data = getattr(data, request_data_attr_name, None)
    print("heres the detail data: ", detail_data)
    if not detail_data:
        raise RequestInfoNotFound()
    request_detail = request_detail_model.model_validate(
        detail_data, update={"request_id": request.id}
    )

    session.add(request_detail)
    session.commit()

    response = RequestDetailResponse.model_validate(request)
    request_detail_response = _get_request_detail_response_model(
        request.request_type
    ).model_validate(request_detail)

    setattr(response, request_data_attr_name, request_detail_response)

    return response


def update_request(
    session: Session, request_id: UUID, data: RequestUpdate, actor: auth_models.User
) -> RequestResponse:
    request = get_request_id(request_id, session)

    if (request.requester_id != actor.id) and (
        actor.role not in [auth_models.UserRole.ADMIN, auth_models.UserRole.STAFF]
    ):
        raise RequestNotAllowed()

    request_detail = get_request_detail(request, session)

    if request.status not in {RequestStatus.NEW, RequestStatus.UNDER_REVIEW}:
        raise RequestCanNotBeUpdated()

    request.more_detail = data.more_detail

    if request.request_type == RequestType.OTHER:
        session.add(request)
        session.commit()
        return RequestDetailResponse.model_validate(request)

    detail_attr = _get_request_detail_attribute_name(request.request_type)
    detail_update_data = getattr(data, detail_attr)
    if detail_update_data is not None:
        request_detail.sqlmodel_update(
            detail_update_data.model_dump(exclude_unset=True)
        )

    session.add(request)
    session.add(request_detail)
    session.commit()
    session.refresh(request)
    session.refresh(request_detail)

    response = RequestDetailResponse.model_validate(request)
    request_detail_response = _get_request_detail_response_model(
        request.request_type
    ).model_validate(request_detail)

    setattr(response, detail_attr, request_detail_response)

    return response


def get_user_request_stats(
    actor: auth_models.User, user_id: UUID, session: Session
) -> UserStatsResponse:
    if actor.id != user_id and (
        actor.role not in [auth_models.UserRole.ADMIN, auth_models.UserRole.STAFF]
    ):
        raise RequestNotAllowed()

    statement = select(
        func.count().label("total"),
        func.sum(case((Request.status == RequestStatus.COMPLETED, 1), else_=0)).label(
            "completed"
        ),
        func.sum(
            case(
                (
                    Request.status.in_(
                        [
                            RequestStatus.NEW,
                            RequestStatus.UNDER_REVIEW,
                            RequestStatus.ASSIGNED,
                        ]
                    ),
                    1,
                ),
                else_=0,
            ),
        ).label("pending"),
    ).where(Request.requester_id == user_id)

    result = session.exec(statement).one()

    return UserStatsResponse(
        user_id=user_id,
        total_requests=result.total or 0,
        pending_requests=result.pending or 0,
        completed_requests=result.completed or 0,
    )


def get_my_requests(
    session: Session, actor: auth_models.User, filters: RequestFilters
) -> list[Request]:
    if actor.role in {auth_models.UserRole.STAFF, auth_models.UserRole.ADMIN}:
        raise StaffNotAllowed()

    statement = (
        select(Request)
        .where(Request.is_deleted == False)
        .where(Request.requester_id == actor.id)
    )

    if filters.request_type:
        statement = statement.where(Request.request_type == filters.request_type)
    if filters.exclude_cancelled:
        statement = statement.where(Request.status != RequestStatus.CANCELLED)

    statement = _sort_requests_statement(filters.sorting, statement)

    statement = statement.limit(filters.limit).offset(filters.offset)

    return session.exec(statement).all()


def _sort_requests_statement(
    sort_option: RequestSortOptions, requests_statement: Select
):
    if sort_option == RequestSortOptions.oldest_first:
        new_statement = requests_statement.order_by(Request.created_at)
    else:
        new_statement = requests_statement.order_by(desc(Request.created_at))

    return new_statement


def get_request_with_detail(
    session: Session, request_id: UUID, actor: auth_models.User
) -> RequestDetailResponse:
    request = get_request_id(request_id, session)
    if request.requester_id != actor.id and actor.role not in {
        auth_models.UserRole.ADMIN,
        auth_models.UserRole.STAFF,
    }:
        raise RequestNotAllowed()

    response = RequestDetailResponse.model_validate(request)
    if request.request_type == RequestType.OTHER:
        return response

    request_detail = get_request_detail(request, session)
    request_detail_response = _get_request_detail_response_model(
        request.request_type
    ).model_validate(request_detail)

    attr = _get_request_detail_attribute_name(request.request_type)
    setattr(response, attr, request_detail_response)

    return response


def get_request_id(request_id: UUID, session: Session) -> Request:
    request: Request = session.get(Request, request_id)
    if not request:
        raise RequestNotFoundError()
    return request


def get_request_detail(request: Request, session: Session):
    if request.request_type == RequestType.OTHER:
        return request

    model = _get_request_detail_model(request.request_type)
    request_detail = session.exec(
        select(model).where(model.request_id == request.id)
    ).first()
    if not request_detail:
        raise RequestInfoNotFound()

    return request_detail


def cancel_request(session: Session, request_id: UUID, actor: auth_models.User):
    request = get_request_id(request_id, session)

    if request.requester_id != actor.id and actor.role not in {
        auth_models.UserRole.ADMIN,
        auth_models.UserRole.STAFF,
    }:
        raise RequestNotAllowed()
    if request.is_deleted:
        raise RequestNotFoundError()

    request.status = RequestStatus.CANCELLED

    session.add(request)
    session.commit()

    return {"detail": "request cancelled"}
