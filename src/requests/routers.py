from fastapi import  APIRouter

router = APIRouter(prefix="/requests", tags=["requests"])

@router.get("/me")
def my_requests():
    return "MY REQUESTS PAGE"