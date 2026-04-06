from fastapi import Request
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

templates = Jinja2Templates("templates")

def rate_limit_key(request: Request):
    user_id = request.cookies.get("access_token")
    return user_id or get_remote_address(request)

limiter = Limiter(key_func=rate_limit_key, default_limits=["100/minute"])

def rate_limit_handler(request, exc: RateLimitExceeded):
    return templates.TemplateResponse(
        "rate_limit_exceeded.html", context={"request": request, "msg": "Too many requests"}
    )