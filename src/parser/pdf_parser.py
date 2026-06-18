"""PDF text extraction for job descriptions and resumes."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pdfplumber
from PyPDF2 import PdfReader


class PDFExtractionError(RuntimeError):
    """Raised when text cannot be extracted from a PDF."""


def _extract_with_pdfplumber(file_obj: str | Path | BinaryIO) -> str:
    pages: list[str] = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
    return "\n".join(pages).strip()


def _extract_with_pypdf2(file_obj: str | Path | BinaryIO) -> str:
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    reader = PdfReader(file_obj)
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(page for page in pages if page.strip()).strip()


def extract_text_from_pdf(file_obj: str | Path | BinaryIO) -> str:
    """Extract readable text from a PDF using pdfplumber, with PyPDF2 fallback."""

    try:
        text = _extract_with_pdfplumber(file_obj)
    except Exception as exc:
        try:
            text = _extract_with_pypdf2(file_obj)
        except Exception as fallback_exc:
            raise PDFExtractionError(
                f"Unable to extract PDF text: {fallback_exc}"
            ) from exc

    if text:
        return text

    try:
        text = _extract_with_pypdf2(file_obj)
    except Exception as exc:
        raise PDFExtractionError("PDF extraction returned no text.") from exc

    if not text:
        raise PDFExtractionError("PDF extraction returned no text.")
    return text


def extract_text_from_upload(uploaded_file: BinaryIO) -> str:
    """Extract text from a Streamlit uploaded PDF."""

    try:
        uploaded_file.seek(0)
        return extract_text_from_pdf(uploaded_file)
    finally:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

