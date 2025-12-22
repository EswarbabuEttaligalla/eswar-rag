from __future__ import annotations

import asyncio
import os
import uuid
import pandas as pd
import pdfplumber
from fastapi import HTTPException, UploadFile
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.config import settings
from app.utils.file_utils import get_extension, sanitize_filename, validate_upload_file
from app.utils.text_utils import normalize_text


class FileService:
    async def save_upload(self, file: UploadFile) -> tuple[str, int, str]:
        validate_upload_file(file)
        filename = sanitize_filename(file.filename or "file")
        ext = get_extension(filename)
        stored_name = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(settings.UPLOAD_DIR, stored_name)
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

        size = 0
        with open(path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=400, detail="File too large")
                out.write(chunk)

        await file.close()
        return path, size, stored_name

    async def extract_text(self, file_path: str) -> str:
        ext = get_extension(file_path)
        if ext == "pdf":
            text = await asyncio.to_thread(self._extract_pdf_text, file_path)
        elif ext == "docx":
            text = await asyncio.to_thread(self._extract_docx_text, file_path)
        elif ext == "csv":
            text = await asyncio.to_thread(self._extract_csv_text, file_path)
        else:
            text = await asyncio.to_thread(self._extract_txt_text, file_path)
        return normalize_text(text)

    def _extract_pdf_text(self, file_path: str) -> str:
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _extract_docx_text(self, file_path: str) -> str:
        doc = DocxDocument(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _extract_csv_text(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_string(index=False)

    def _extract_txt_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
