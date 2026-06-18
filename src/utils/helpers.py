"""General helper functions for Streamlit and reports."""

from __future__ import annotations

from pathlib import Path


def safe_candidate_name(filename: str) -> str:
    name = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
    return " ".join(part.capitalize() for part in name.split()) or "Unknown Candidate"


def read_text_upload(uploaded_file) -> str:
    uploaded_file.seek(0)
    return uploaded_file.read().decode("utf-8", errors="ignore")


def list_to_label(values: list[str] | set[str], empty: str = "None detected") -> str:
    ordered = sorted(values)
    return ", ".join(ordered) if ordered else empty

