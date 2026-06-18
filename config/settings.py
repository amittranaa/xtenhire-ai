"""Application settings for XtenHire AI."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESUME_DIR = DATA_DIR / "resumes"
JOB_DIR = DATA_DIR / "jobs"
OUTPUT_DIR = DATA_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"

SUPPORTED_FILE_TYPES = ["pdf", "txt"]

SCORE_WEIGHTS = {
    "similarity": 0.50,
    "skill_match": 0.25,
    "experience": 0.15,
    "education": 0.10,
}

MIN_SHORTLIST_SCORE = 75
MIN_REVIEW_SCORE = 55

