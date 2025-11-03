from __future__ import annotations

import os
import re
from typing import Iterable

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_MIME_MAP = {
    "pdf": {"application/pdf"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "txt": {"text/plain"},
    "csv": {"text/csv", "application/vnd.ms-excel"},
}


def ensure_dirs(paths: Iterable[str]) -> None:
    for path in paths:
        os.makedirs(path, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("_")
    return cleaned or "file"


def get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().lstrip(".")


def allowed_extensions() -> set[str]:
    return {ext.strip().lower() for ext in settings.ALLOWED_FILE_TYPES.split(",") if ext.strip()}


def validate_upload_file(file: UploadFile) -> None:
    ext = get_extension(file.filename or "")
    if ext not in allowed_extensions():
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if file.content_type:
        allowed_mimes = ALLOWED_MIME_MAP.get(ext, set())
        if file.content_type in {"application/octet-stream", "binary/octet-stream"}:
            return
        if allowed_mimes and file.content_type not in allowed_mimes:
            raise HTTPException(status_code=400, detail="Invalid content type")
