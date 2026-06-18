"""Skill, experience, education, and summary extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "nosql",
    "mongodb",
    "postgresql",
    "mysql",
    "excel",
    "power bi",
    "tableau",
    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",
    "scikit-learn",
    "sklearn",
    "spaCy",
    "nltk",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "streamlit",
    "flask",
    "django",
    "fastapi",
    "react",
    "node.js",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "github",
    "rest api",
    "api",
    "data analysis",
    "data visualization",
    "statistics",
    "communication",
    "leadership",
    "project management",
    "agile",
    "scrum",
}

EDUCATION_LEVELS = {
    "phd": 100,
    "doctorate": 100,
    "masters": 90,
    "master": 90,
    "m.tech": 90,
    "mtech": 90,
    "mba": 85,
    "bachelor": 75,
    "b.tech": 75,
    "btech": 75,
    "b.e": 75,
    "be": 75,
    "bsc": 70,
    "degree": 65,
    "diploma": 55,
}


@dataclass(frozen=True)
class CandidateSignals:
    skills: set[str]
    years_experience: float
    education_score: float
    summary: str


def _canonical_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def extract_skills(text: str, skills_library: set[str] | None = None) -> set[str]:
    """Extract known technical and professional skills from free text."""

    library = skills_library or DEFAULT_SKILLS
    haystack = _canonical_text(text)
    found: set[str] = set()

    for skill in library:
        needle = skill.lower()
        pattern = r"(?<![a-z0-9+#.])" + re.escape(needle) + r"(?![a-z0-9+#])"
        if re.search(pattern, haystack):
            found.add(skill)

    if "natural language processing" in found:
        found.add("nlp")
    if "sklearn" in found:
        found.add("scikit-learn")
    return found


def extract_years_experience(text: str) -> float:
    """Estimate years of experience from common resume/JD phrasing."""

    haystack = _canonical_text(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+in",
    ]
    values: list[float] = []
    for pattern in patterns:
        values.extend(float(match) for match in re.findall(pattern, haystack))
    return max(values) if values else 0.0


def extract_education_score(text: str) -> float:
    """Score the highest detected education signal on a 0-100 scale."""

    haystack = _canonical_text(text)
    score = 0
    for keyword, value in EDUCATION_LEVELS.items():
        pattern = r"(?<![a-z0-9.])" + re.escape(keyword) + r"(?![a-z0-9.])"
        if re.search(pattern, haystack):
            score = max(score, value)
    return float(score)


def summarize_resume(text: str, max_sentences: int = 3) -> str:
    """Create a short extractive resume summary."""

    sentences = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    useful = [sentence.strip() for sentence in sentences if len(sentence.split()) >= 6]
    return " ".join(useful[:max_sentences])[:700]


def extract_candidate_signals(text: str) -> CandidateSignals:
    return CandidateSignals(
        skills=extract_skills(text),
        years_experience=extract_years_experience(text),
        education_score=extract_education_score(text),
        summary=summarize_resume(text),
    )
