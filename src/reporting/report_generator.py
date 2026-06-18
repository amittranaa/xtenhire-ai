"""Generate CSV, JSON, and text hiring reports."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config.settings import OUTPUT_DIR
from src.scoring.score_engine import CandidateScore


def scores_to_dataframe(scores: list[CandidateScore]) -> pd.DataFrame:
    rows = [score.to_dict() for score in scores]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df[
        [
            "rank",
            "candidate",
            "final_score",
            "status",
            "similarity_score",
            "skill_match_score",
            "experience_score",
            "education_score",
            "years_experience",
            "skills_found",
            "missing_skills",
            "recommendation",
            "summary",
        ]
    ]


def save_csv_report(scores: list[CandidateScore], filename: str = "candidate_ranking.csv") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    scores_to_dataframe(scores).to_csv(path, index=False)
    return path


def save_json_report(scores: list[CandidateScore], filename: str = "candidate_report.json") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps([score.to_dict() for score in scores], indent=2), encoding="utf-8")
    return path


def generate_hiring_report(scores: list[CandidateScore]) -> str:
    if not scores:
        return "No candidates were ranked."

    lines = ["XtenHire AI Hiring Report", "", "Top Candidates:"]
    for score in scores[:5]:
        lines.append(
            f"{score.rank}. {score.candidate} - {score.final_score}/100 "
            f"({score.status}) | {score.recommendation}"
        )
    return "\n".join(lines)

