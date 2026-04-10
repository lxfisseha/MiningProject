from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from uuid import UUID
from src.database import SESSION_DEP
from src.utils import nest_dotted_form_data

from src.auth.services import get_user_by_id
from .profile_documents import get_profile_documents_service
from .services import DocumentService
from .storage import FileStorageService

router = APIRouter(prefix="/documents", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.post("/profile/{user_id}")
async def profile_documents_upload(
    request: Request, user_id: UUID,
    session: SESSION_DEP,
        ):
    user = get_user_by_id(user_id, session) 
    data = await request.form()
    form_data = nest_dotted_form_data(data)

    profile_docs_service = get_profile_documents_service(document_service=DocumentService(FileStorageService()))
    await profile_docs_service.save_profile_documents(form_data, session, user)

    return templates.TemplateResponse(
        "profiles/_file_upload_success_response.html",
        {"request": request, "msg": "Documents uploaded successfully!"}
    )  

