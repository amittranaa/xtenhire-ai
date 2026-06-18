"""Weighted ATS scoring engine for XtenHire AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from config.settings import MIN_REVIEW_SCORE, MIN_SHORTLIST_SCORE, SCORE_WEIGHTS
from src.extractor.skill_extractor import (
    extract_candidate_signals,
    extract_education_score,
    extract_skills,
    extract_years_experience,
)
from src.scoring.tfidf_ranker import TfidfRanker


@dataclass(frozen=True)
class CandidateScore:
    rank: int
    candidate: str
    final_score: float
    similarity_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    status: str
    skills_found: list[str]
    missing_skills: list[str]
    years_experience: float
    summary: str
    recommendation: str

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_skill_match(required_skills: set[str], candidate_skills: set[str]) -> float:
    if not required_skills:
        return 100.0 if candidate_skills else 0.0
    return round((len(required_skills & candidate_skills) / len(required_skills)) * 100, 2)


def calculate_experience_match(required_years: float, candidate_years: float) -> float:
    if required_years <= 0:
        return 100.0 if candidate_years > 0 else 70.0
    return round(min(candidate_years / required_years, 1.0) * 100, 2)


def calculate_education_match(required_score: float, candidate_score: float) -> float:
    if required_score <= 0:
        return 100.0 if candidate_score > 0 else 70.0
    return round(min(candidate_score / required_score, 1.0) * 100, 2)


def weighted_score(
    similarity_score: float,
    skill_match_score: float,
    experience_score: float,
    education_score: float,
) -> float:
    score = (
        similarity_score * SCORE_WEIGHTS["similarity"]
        + skill_match_score * SCORE_WEIGHTS["skill_match"]
        + experience_score * SCORE_WEIGHTS["experience"]
        + education_score * SCORE_WEIGHTS["education"]
    )
    return round(score, 2)


def get_status(score: float) -> str:
    if score >= MIN_SHORTLIST_SCORE:
        return "Shortlist"
    if score >= MIN_REVIEW_SCORE:
        return "Review"
    return "Reject"


def build_recommendation(score: float, missing_skills: list[str], exp_score: float) -> str:
    if score >= MIN_SHORTLIST_SCORE and not missing_skills:
        return "Strong fit. Prioritize for interview."
    if score >= MIN_SHORTLIST_SCORE:
        return f"Strong profile with gaps in {', '.join(missing_skills[:3])}."
    if score >= MIN_REVIEW_SCORE:
        if exp_score < 60:
            return "Promising skills, but experience appears below requirement."
        return "Potential fit. Review resume details before screening."
    return "Low match for this role based on current JD requirements."


def rank_candidates(job_description: str, resumes: dict[str, str]) -> list[CandidateScore]:
    """Rank candidates using similarity, skills, experience, and education signals."""

    required_skills = extract_skills(job_description)
    required_years = extract_years_experience(job_description)
    required_education = extract_education_score(job_description)
    similarity_results = TfidfRanker().score(job_description, resumes)
    similarity_by_name = {result.name: result.similarity_score for result in similarity_results}

    scored: list[CandidateScore] = []
    for candidate, resume_text in resumes.items():
        signals = extract_candidate_signals(resume_text)
        skill_score = calculate_skill_match(required_skills, signals.skills)
        experience_score = calculate_experience_match(required_years, signals.years_experience)
        education_score = calculate_education_match(required_education, signals.education_score)
        final = weighted_score(
            similarity_by_name.get(candidate, 0.0),
            skill_score,
            experience_score,
            education_score,
        )
        missing = sorted(required_skills - signals.skills)
        scored.append(
            CandidateScore(
                rank=0,
                candidate=candidate,
                final_score=final,
                similarity_score=similarity_by_name.get(candidate, 0.0),
                skill_match_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                status=get_status(final),
                skills_found=sorted(signals.skills),
                missing_skills=missing,
                years_experience=signals.years_experience,
                summary=signals.summary,
                recommendation=build_recommendation(final, missing, experience_score),
            )
        )

    ranked = sorted(scored, key=lambda item: item.final_score, reverse=True)
    return [
        CandidateScore(**{**candidate.to_dict(), "rank": index})
        for index, candidate in enumerate(ranked, start=1)
    ]

