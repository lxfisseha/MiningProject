from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from uuid import UUID
from src.database import SESSION_DEP
from src.utils import nest_dotted_form_data

from src.auth.services import get_user_by_id
from src.auth.dependencies import CURRENT_USER_FROM_COOKIE
from src.profiles.services import get_profile_by_user

from .profile_documents import get_profile_documents_service
from .services import DocumentService
from .storage import FileStorageService

from pathlib import Path
import mimetypes


router = APIRouter(prefix="/documents", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.post("/profile/{user_id}")
async def profile_documents_upload(
    request: Request,
    user_id: UUID,
    session: SESSION_DEP,
):
    user = get_user_by_id(user_id, session) 
    data = await request.form()
    form_data = nest_dotted_form_data(data)

    profile_docs_service = get_profile_documents_service(document_service=DocumentService(FileStorageService()))
    await profile_docs_service.save_profile_documents(form_data, session, user, get_profile_by_user(user, session))

    return templates.TemplateResponse(
        "profiles/_file_upload_success_response.html",
        {"request": request, "msg": "Documents uploaded successfully!"}
    )  

@router.get("/documents/{document_id}/download")
def download_document(
    document_id: UUID,
    session: SESSION_DEP,
    current_user: CURRENT_USER_FROM_COOKIE,
):
    document_service = DocumentService(FileStorageService())
    file, document = document_service.get_document_file(
        db=session,
        document_id=document_id,
        current_user=current_user,
    )

    filename = Path(document.file_path).name
    media_type, _ = mimetypes.guess_type(filename)

    return StreamingResponse(
        file,
        media_type=media_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )