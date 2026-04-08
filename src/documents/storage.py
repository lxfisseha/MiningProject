import uuid
from pathlib import Path
from fastapi import UploadFile
from .schemas import (
    FileSaveRequest,
    FileSaveResponse,
    FileDeleteRequest,
    FileReadRequest,
)


class FileStorageService:
    def __init__(self, base_dir: Path = Path("uploads")):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> str:
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"

    def _generate_path(self, subdir: str, filename: str) -> Path:
        dir_path = self.base_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / filename

    async def save(
        self,
        file: UploadFile,
        data: FileSaveRequest
    ) -> FileSaveResponse:

        allowed_types = ["application/pdf", "image/jpeg", "image/png"]
        if data.content_type not in allowed_types:
            raise ValueError("Unsupported file type")

        filename = self._generate_filename(data.filename)
        file_path = self._generate_path(data.subdir or "", filename)

        size = 0

        # Stream write (important)
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if data.max_size and size > data.max_size:
                    buffer.close()
                    file_path.unlink(missing_ok=True)
                    raise ValueError("File too large")

                buffer.write(chunk)

        return FileSaveResponse(
            file_path=str(file_path),
            file_name=filename,
            content_type=data.content_type,
            size=size,
        )

    def delete(self, data: FileDeleteRequest) -> None:
        path = Path(data.file_path)

        if path.exists() and path.is_file():
            path.unlink()

    def open(self, data: FileReadRequest):
        path = Path(data.file_path)

        if not path.exists():
            raise FileNotFoundError("File not found")

        return open(path, "rb")