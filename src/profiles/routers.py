from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/profile/me")
async def get_my_profile():
    pass
