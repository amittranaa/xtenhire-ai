from src.extractor.skill_extractor import (
    extract_education_score,
    extract_skills,
    extract_years_experience,
)


def test_extract_skills_detects_multi_word_skills():
    text = "Built Natural Language Processing systems with Python and Power BI."

    skills = extract_skills(text)

    assert "python" in skills
    assert "natural language processing" in skills
    assert "nlp" in skills
    assert "power bi" in skills


def test_extract_years_experience_reads_common_patterns():
    assert extract_years_experience("I have 5+ years of experience in Python.") == 5
    assert extract_years_experience("Experience: 2 years with analytics.") == 2


def test_extract_education_score_uses_highest_detected_level():
    text = "Bachelor in Computer Science. MBA in Business Analytics."

    assert extract_education_score(text) == 85

