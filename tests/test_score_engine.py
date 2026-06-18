from src.scoring.score_engine import (
    calculate_education_match,
    calculate_experience_match,
    calculate_skill_match,
    rank_candidates,
    weighted_score,
)


def test_weighted_score_uses_project_formula():
    assert weighted_score(90, 80, 70, 100) == 85.5


def test_skill_match_scores_required_skills():
    required = {"python", "sql", "streamlit"}
    candidate = {"python", "sql", "react"}

    assert calculate_skill_match(required, candidate) == 66.67


def test_experience_match_caps_at_100():
    assert calculate_experience_match(3, 5) == 100.0
    assert calculate_experience_match(4, 2) == 50.0


def test_education_match_handles_missing_requirement():
    assert calculate_education_match(0, 75) == 100.0
    assert calculate_education_match(90, 75) == 83.33


def test_rank_candidates_prefers_stronger_resume():
    jd = """
    We need a Python developer with SQL, Streamlit, NLP, scikit-learn,
    machine learning, 3 years experience, and a bachelor degree.
    """
    resumes = {
        "Amit": """
        Python developer with 4 years experience building Streamlit apps.
        Skilled in SQL, NLP, scikit-learn, pandas, and machine learning.
        Bachelor of Technology in Computer Science.
        """,
        "Rahul": """
        Frontend engineer with React and JavaScript experience. Built landing
        pages and design systems. Diploma in design.
        """,
    }

    ranked = rank_candidates(jd, resumes)

    assert ranked[0].candidate == "Amit"
    assert ranked[0].rank == 1
    assert ranked[0].final_score > ranked[1].final_score
    assert "python" in ranked[0].skills_found
    assert ranked[0].status in {"Shortlist", "Review"}

