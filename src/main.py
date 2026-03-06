from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from .exceptions import BaseException
from src.auth.routers import router as auth_api_routers

app = FastAPI()

app.include_router(auth_api_routers)


@app.exception_handler(BaseException)
async def base_exception_handler_for_htmx(request: Request, exp: BaseException):
    return HTMLResponse(content=exp.message, status_code=200)


@app.get("/")
def home():
    return "Hello world"
