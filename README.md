# XtenHire AI

**Hire Smarter. Rank Faster.**

XtenHire AI is a mini ATS (Applicant Tracking System) for resume intelligence and candidate ranking. HR uploads a job description, uploads multiple resumes, and receives AI-assisted ranking, skill gaps, candidate insights, analytics, and exportable hiring reports.

## Features

- Upload job descriptions as PDF, TXT, or pasted text
- Upload multiple resumes as PDF or TXT
- Extract PDF text with `pdfplumber` and `PyPDF2` fallback
- Clean resume/JD text with spaCy and NLTK
- Rank resumes with TF-IDF cosine similarity
- Extract skills, experience, and education signals
- Calculate an ATS score using weighted scoring
- Show candidate insights, missing skills, recommendations, and interview questions
- Visualize top skills, score breakdowns, and skill gaps with Plotly
- Premium dark enterprise SaaS dashboard with glass surfaces, seven-screen sidebar navigation, KPI metrics, responsive ranking rows, and recruiter analytics
- Candidate detail workflow with ATS progress rings, fit radar charts, skill comparison, and hiring recommendations
- Job description analyzer with skill tags and keyword intelligence
- Premium multi-file resume intake with parsing progress and file previews
- Export CSV rankings and a text hiring report

## Scoring Formula

Final Score =

- 50% Resume Similarity
- 25% Skill Match
- 15% Experience Match
- 10% Education Match

Example:

```text
Similarity = 90
Skill Match = 80
Experience = 70
Education = 100

Final Score = (90 * 0.50) + (80 * 0.25) + (70 * 0.15) + (100 * 0.10)
Final Score = 85.5
```

## Project Structure

```text
xtenhire-ai/
├── app.py
├── config/
│   └── settings.py
├── data/
│   ├── resumes/
│   ├── jobs/
│   └── outputs/
├── models/
│   └── vectorizer.pkl
├── src/
│   ├── parser/
│   │   └── pdf_parser.py
│   ├── preprocessing/
│   │   └── text_cleaner.py
│   ├── extractor/
│   │   └── skill_extractor.py
│   ├── scoring/
│   │   ├── tfidf_ranker.py
│   │   └── score_engine.py
│   ├── reporting/
│   │   └── report_generator.py
│   └── utils/
│       └── helpers.py
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

Use Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

The app can run without `en_core_web_sm`; it falls back to `spacy.blank("en")`. Installing the model improves tokenization and lemmatization.

## Run the App

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Run Tests

```bash
pytest
```

## Deployment

For Streamlit Cloud:

1. Push this repository to GitHub.
2. Create a new Streamlit Cloud app.
3. Set the main file path to `app.py`.
4. Ensure `requirements.txt` is included.

## Notes

This project intentionally goes beyond a basic TF-IDF demo. TF-IDF similarity is one feature inside a broader ATS scoring engine that also evaluates skills, experience, education, recommendations, analytics, and hiring reports.
