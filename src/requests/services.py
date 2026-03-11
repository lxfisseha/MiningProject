from pydantic import BaseModel


from uuid import UUID



class UserStatsResponse(BaseModel):
    user_id: UUID
    total_requests: int | None = 0
    pending_requests: int | None = 0
    completed_requests: int | None = 0


def get_user_request_stats(actor, user_id , session):
    return UserStatsResponse(user_id=user_id, total_requests=4, pending_requests=4, completed_requests=4)