"""Streamlit dashboard for XtenHire AI."""

from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.extractor.skill_extractor import extract_skills
from src.parser.pdf_parser import PDFExtractionError, extract_text_from_upload
from src.reporting.report_generator import generate_hiring_report, scores_to_dataframe
from src.scoring.score_engine import rank_candidates
from src.utils.helpers import read_text_upload, safe_candidate_name


st.set_page_config(
    page_title="XtenHire AI",
    page_icon="X",
    layout="wide",
    initial_sidebar_state="expanded",
)


PLOTLY_TEMPLATE = "plotly_dark"
NAV_ITEMS = [
    "Dashboard",
    "Candidates",
    "Resume Screening",
    "Job Descriptions",
    "Analytics",
    "Reports",
    "Settings",
]


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0B1020;
                --surface: #111827;
                --surface-2: #151f32;
                --surface-3: rgba(17, 24, 39, 0.76);
                --border: rgba(255, 255, 255, 0.08);
                --border-strong: rgba(255, 255, 255, 0.16);
                --text: #F8FAFC;
                --muted: #94A3B8;
                --blue: #2563eb;
                --purple: #7C3AED;
                --success: #10B981;
                --warning: #F59E0B;
                --danger: #EF4444;
                --shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
                --radius: 8px;
            }

            .stApp {
                background: linear-gradient(180deg, #0B1020 0%, #0b1020 45%, #080c18 100%);
                color: var(--text);
                font-family: Inter, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
            }

            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 3rem;
                max-width: 1440px;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(11, 16, 32, 0.98));
                border-right: 1px solid var(--border);
                box-shadow: 16px 0 54px rgba(0, 0, 0, 0.28);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {
                color: #CBD5E1;
            }

            [data-testid="stSidebar"] [role="radiogroup"] label {
                border-radius: 8px;
                padding: 0.45rem 0.55rem;
                margin: 0.15rem 0;
                transition: background 160ms ease, transform 160ms ease;
            }

            [data-testid="stSidebar"] [role="radiogroup"] label:hover {
                background: rgba(255, 255, 255, 0.06);
                transform: translateX(2px);
            }

            h1, h2, h3 {
                letter-spacing: 0;
            }

            h1 {
                color: var(--text);
                font-size: 2.45rem;
                line-height: 1.05;
                margin-bottom: 0.25rem;
            }

            h2, h3 {
                color: var(--text);
            }

            div[data-testid="stMetric"] {
                background: rgba(17, 24, 39, 0.72);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 1rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
            }

            div[data-testid="stMetricLabel"] p {
                color: var(--muted);
                font-size: 0.82rem;
            }

            div[data-testid="stMetricValue"] {
                color: var(--text);
                font-weight: 750;
            }

            .topbar {
                display: grid;
                grid-template-columns: minmax(220px, 1fr) auto auto;
                align-items: center;
                gap: 1rem;
                background: rgba(17, 24, 39, 0.70);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 0.75rem 0.9rem;
                margin-bottom: 1rem;
                backdrop-filter: blur(18px);
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.22);
            }

            .topbar-search {
                color: var(--muted);
                background: rgba(255, 255, 255, 0.045);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 0.68rem 0.85rem;
            }

            .topbar-actions {
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }

            .topbar-link {
                min-height: 38px;
                border-radius: 8px;
                display: inline-flex;
                align-items: center;
                color: #E2E8F0;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid var(--border);
                padding: 0 0.75rem;
                font-size: 0.78rem;
                font-weight: 700;
            }

            .profile-chip {
                display: flex;
                align-items: center;
                gap: 0.55rem;
                color: #E2E8F0;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.38rem 0.7rem 0.38rem 0.4rem;
                font-size: 0.86rem;
            }

            .avatar {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                color: white;
                font-size: 0.75rem;
                font-weight: 800;
                background: linear-gradient(135deg, var(--blue), var(--purple));
            }

            .brand-shell {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                padding: 0.75rem 0 1.25rem;
            }

            .brand-mark {
                width: 44px;
                height: 44px;
                display: grid;
                place-items: center;
                border-radius: 8px;
                background: linear-gradient(135deg, var(--blue), var(--purple));
                color: white;
                font-weight: 800;
                box-shadow: 0 18px 42px rgba(79, 70, 229, 0.34);
            }

            .brand-title {
                margin: 0;
                color: var(--text);
                font-size: 1rem;
                font-weight: 800;
            }

            .brand-subtitle {
                margin: 0.1rem 0 0;
                color: var(--muted);
                font-size: 0.78rem;
            }

            .hero-panel {
                position: relative;
                overflow: hidden;
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 1.55rem 1.7rem;
                background:
                    linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(124, 58, 237, 0.18)),
                    rgba(17, 24, 39, 0.78);
                box-shadow: var(--shadow);
                backdrop-filter: blur(22px);
                margin-bottom: 1.1rem;
            }

            .eyebrow {
                color: #93C5FD;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.45rem;
            }

            .hero-copy {
                color: #CBD5E1;
                max-width: 820px;
                margin: 0.45rem 0 0;
                font-size: 0.98rem;
            }

            .glass-card {
                background: rgba(17, 24, 39, 0.74);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 1.05rem;
                box-shadow: 0 18px 54px rgba(0, 0, 0, 0.22);
                backdrop-filter: blur(18px);
                margin-bottom: 1rem;
                transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
            }

            .section-header {
                padding: 0.45rem 0 0.65rem;
                margin-top: 0.35rem;
            }

            .glass-card:hover,
            .kpi-card:hover,
            .candidate-row:hover {
                transform: translateY(-2px);
                border-color: rgba(255, 255, 255, 0.18);
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.32);
            }

            .upload-panel {
                position: relative;
                border: 1px dashed rgba(147, 197, 253, 0.46);
                border-radius: 8px;
                padding: 1rem;
                background:
                    linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(124, 58, 237, 0.11)),
                    rgba(17, 24, 39, 0.64);
                margin-bottom: 1rem;
            }

            .section-title {
                color: var(--text);
                font-size: 1rem;
                font-weight: 750;
                margin-bottom: 0.25rem;
            }

            .muted {
                color: var(--muted);
                font-size: 0.9rem;
                margin: 0;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                padding: 0.24rem 0.62rem;
                border-radius: 999px;
                background: rgba(37, 99, 235, 0.13);
                border: 1px solid rgba(147, 197, 253, 0.22);
                color: #BFDBFE;
                font-size: 0.82rem;
                margin: 0.18rem 0.18rem 0 0;
            }

            .status-shortlist { color: var(--green); font-weight: 800; }
            .status-review { color: var(--amber); font-weight: 800; }
            .status-reject { color: var(--red); font-weight: 800; }

            div[data-testid="stDataFrame"] {
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid var(--border);
                box-shadow: 0 18px 54px rgba(0, 0, 0, 0.22);
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 8px;
                border: 1px solid rgba(147, 197, 253, 0.24);
                background: linear-gradient(135deg, var(--blue), var(--purple));
                color: white;
                font-weight: 700;
                box-shadow: 0 14px 34px rgba(37, 99, 235, 0.26);
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: #1e40af;
                color: white;
                box-shadow: 0 10px 24px rgba(37, 99, 235, 0.26);
            }

            textarea, input, [data-testid="stFileUploader"] {
                border-radius: 8px;
            }

            textarea,
            input {
                background: rgba(255, 255, 255, 0.055) !important;
                color: var(--text) !important;
                border-color: var(--border) !important;
            }

            [data-testid="stFileUploader"] section {
                background: rgba(17, 24, 39, 0.72);
                border: 1px dashed rgba(147, 197, 253, 0.46);
                border-radius: 8px;
            }

            .stAlert {
                border-radius: 8px;
            }

            div[data-testid="stExpander"] {
                background: rgba(17, 24, 39, 0.72);
                border: 1px solid var(--border);
                border-radius: 8px;
            }

            hr {
                border-color: var(--border);
            }

            .kpi-card {
                position: relative;
                overflow: hidden;
                min-height: 136px;
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.02)),
                    rgba(17, 24, 39, 0.78);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 1rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
                transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
            }

            .kpi-card::before {
                content: "";
                position: absolute;
                inset: 0 auto 0 0;
                width: 3px;
                background: linear-gradient(180deg, var(--blue), var(--purple));
            }

            .kpi-label {
                color: var(--muted);
                font-size: 0.82rem;
                font-weight: 650;
            }

            .kpi-value {
                color: var(--text);
                font-size: 2rem;
                line-height: 1.1;
                font-weight: 820;
                margin-top: 0.25rem;
            }

            .kpi-delta {
                color: #CBD5E1;
                font-size: 0.78rem;
                margin-top: 0.5rem;
            }

            .candidate-row {
                display: grid;
                grid-template-columns: 54px minmax(160px, 1.35fr) 112px repeat(2, minmax(110px, 0.8fr)) minmax(190px, 1.4fr) 150px;
                gap: 0.8rem;
                align-items: center;
                background: rgba(17, 24, 39, 0.72);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 0.85rem;
                margin-bottom: 0.72rem;
                box-shadow: 0 14px 42px rgba(0, 0, 0, 0.18);
                transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
            }

            .candidate-header {
                color: var(--muted);
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin: 0.6rem 0;
            }

            .candidate-name {
                color: var(--text);
                font-weight: 760;
            }

            .candidate-meta {
                color: var(--muted);
                font-size: 0.78rem;
                margin-top: 0.15rem;
            }

            .score-ring {
                --score: 0;
                width: 58px;
                height: 58px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                background:
                    radial-gradient(closest-side, #111827 72%, transparent 74%),
                    conic-gradient(var(--success) calc(var(--score) * 1%), rgba(255,255,255,0.08) 0);
                color: var(--text);
                font-weight: 820;
                font-size: 0.86rem;
                animation: fadeUp 420ms ease both;
            }

            .mini-meter {
                height: 8px;
                border-radius: 999px;
                overflow: hidden;
                background: rgba(255, 255, 255, 0.08);
                margin-top: 0.35rem;
            }

            .mini-meter span {
                display: block;
                height: 100%;
                border-radius: inherit;
                background: linear-gradient(90deg, var(--blue), var(--purple));
            }

            .status-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: fit-content;
                border-radius: 999px;
                padding: 0.34rem 0.68rem;
                font-size: 0.78rem;
                font-weight: 760;
                border: 1px solid transparent;
            }

            .badge-strong {
                color: #A7F3D0;
                background: rgba(16, 185, 129, 0.12);
                border-color: rgba(16, 185, 129, 0.22);
            }

            .badge-interview {
                color: #BFDBFE;
                background: rgba(37, 99, 235, 0.14);
                border-color: rgba(37, 99, 235, 0.24);
            }

            .badge-review {
                color: #FCD34D;
                background: rgba(245, 158, 11, 0.12);
                border-color: rgba(245, 158, 11, 0.22);
            }

            .badge-rejected {
                color: #FCA5A5;
                background: rgba(239, 68, 68, 0.12);
                border-color: rgba(239, 68, 68, 0.22);
            }

            .drawer-grid {
                display: grid;
                grid-template-columns: 0.9fr 1.1fr;
                gap: 1rem;
                align-items: start;
            }

            .upload-visual {
                display: grid;
                place-items: center;
                gap: 0.55rem;
                text-align: center;
                min-height: 152px;
                border: 1px dashed rgba(147, 197, 253, 0.48);
                border-radius: 8px;
                background: rgba(255,255,255,0.035);
            }

            .upload-orb {
                width: 46px;
                height: 46px;
                border-radius: 8px;
                display: grid;
                place-items: center;
                background: linear-gradient(135deg, var(--blue), var(--purple));
                color: white;
                box-shadow: 0 16px 38px rgba(79, 70, 229, 0.30);
                animation: pulseSoft 2.4s ease-in-out infinite;
            }

            .progress-track {
                height: 8px;
                border-radius: 999px;
                background: rgba(255,255,255,0.08);
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                border-radius: inherit;
                background: linear-gradient(90deg, var(--blue), var(--purple));
            }

            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes pulseSoft {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-4px); }
            }

            @media (max-width: 760px) {
                .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                h1 {
                    font-size: 1.75rem;
                }

                .hero-panel,
                .glass-card {
                    border-radius: 8px;
                    padding: 1rem;
                }

                .topbar {
                    grid-template-columns: 1fr;
                }

                .candidate-row,
                .drawer-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "job_description": "",
        "resumes": {},
        "scores": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def parse_uploaded_resume(uploaded_file) -> tuple[str, str] | None:
    candidate = safe_candidate_name(uploaded_file.name)
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            text = extract_text_from_upload(uploaded_file)
        else:
            text = read_text_upload(uploaded_file)
    except (PDFExtractionError, UnicodeDecodeError) as exc:
        st.error(f"Could not parse {uploaded_file.name}: {exc}")
        return None
    return candidate, text


def run_ranking() -> None:
    if not st.session_state.job_description.strip():
        st.warning("Upload or paste a job description first.")
        return
    if not st.session_state.resumes:
        st.warning("Upload at least one resume.")
        return
    st.session_state.scores = rank_candidates(
        st.session_state.job_description,
        st.session_state.resumes,
    )


def status_label(score) -> tuple[str, str]:
    if score.final_score >= 85:
        return "Strong Match", "badge-strong"
    if score.final_score >= 75:
        return "Interview Recommended", "badge-interview"
    if score.final_score >= 55:
        return "Needs Review", "badge-review"
    return "Rejected", "badge-rejected"


def render_topbar() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-search">Search candidates, skills, jobs, or reports...</div>
            <div class="topbar-actions">
                <div class="topbar-link">Quick search</div>
                <div class="topbar-link">Notifications</div>
            </div>
            <div class="profile-chip">
                <div class="avatar">HR</div>
                <span>Hiring Team</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    st.sidebar.markdown(
        """
        <div class="brand-shell">
            <div class="brand-mark">X</div>
            <div>
                <p class="brand-title">XtenHire AI</p>
                <p class="brand-subtitle">Hire Smarter. Rank Faster.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio(
        "Workspace",
        NAV_ITEMS,
    )
    st.sidebar.markdown("---")
    st.sidebar.metric("Candidates", len(st.session_state.resumes))
    st.sidebar.metric("Ranked", len(st.session_state.scores))
    st.sidebar.caption("ATS Score: 50% Similarity + 25% Skill + 15% Experience + 10% Education")
    return page


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="eyebrow">AI-Powered Resume Intelligence</div>
            <h1>{title}</h1>
            <p class="hero-copy">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, subtitle: str | None = None) -> None:
    subtitle_markup = f'<p class="muted">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{title}</div>
            {subtitle_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_visual(title: str, subtitle: str, progress: int = 0) -> None:
    st.markdown(
        f"""
        <div class="upload-visual">
            <div class="upload-orb">ADD</div>
            <div>
                <div class="section-title">{escape(title)}</div>
                <p class="muted">{escape(subtitle)}</p>
            </div>
            <div style="width: min(320px, 82%);" class="progress-track">
                <div class="progress-fill" style="width: {max(0, min(progress, 100))}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_pills(skills: list[str] | set[str], empty: str = "None detected") -> None:
    if not skills:
        st.caption(empty)
        return
    pills = "".join(f'<span class="pill">{skill}</span>' for skill in sorted(skills))
    st.markdown(pills, unsafe_allow_html=True)


def score_dataframe(scores) -> pd.DataFrame:
    if not scores:
        return pd.DataFrame()
    return scores_to_dataframe(scores)


def calculate_kpis() -> dict[str, float | int | str]:
    scores = st.session_state.scores
    avg_score = round(sum(score.final_score for score in scores) / len(scores), 1) if scores else 0
    shortlisted = sum(score.status == "Shortlist" for score in scores)
    required_skills = extract_skills(st.session_state.job_description) if st.session_state.job_description else set()
    top_candidate = scores[0].candidate if scores else "Not ranked"
    return {
        "jd_words": len(st.session_state.job_description.split()),
        "candidates": len(st.session_state.resumes),
        "avg_score": avg_score,
        "shortlisted": shortlisted,
        "required_skills": len(required_skills),
        "top_candidate": top_candidate,
    }


def render_kpis() -> None:
    kpis = calculate_kpis()
    items = [
        ("Total Candidates", kpis["candidates"], "Active pipeline volume"),
        ("Average ATS Score", kpis["avg_score"], "Weighted match quality"),
        ("Strong Matches", kpis["shortlisted"], "Ready for recruiter review"),
        ("Open Positions", 1 if st.session_state.job_description else 0, "JD intake status"),
    ]
    cols = st.columns(4)
    for col, (label, value, delta) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-delta">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def style_plotly(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.35)",
        font={"color": "#CBD5E1"},
        title={"font": {"color": "#F8FAFC", "size": 18}},
        legend={"bgcolor": "rgba(0,0,0,0)"},
        margin={"l": 24, "r": 24, "t": 58, "b": 36},
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    return fig


def render_candidate_rows(scores) -> None:
    st.markdown(
        """
        <div class="candidate-header candidate-row" style="background: transparent; box-shadow: none; border-color: transparent; padding-bottom: 0;">
            <div>Rank</div>
            <div>Candidate</div>
            <div>ATS Score</div>
            <div>Skills Match</div>
            <div>Experience</div>
            <div>Recommendation</div>
            <div>Status</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for score in scores:
        label, klass = status_label(score)
        st.markdown(
            f"""
            <div class="candidate-row">
                <div class="candidate-name">#{score.rank}</div>
                <div>
                    <div class="candidate-name">{escape(score.candidate)}</div>
                    <div class="candidate-meta">{len(score.skills_found)} skills matched | {score.years_experience:g} yrs exp</div>
                </div>
                <div class="score-ring" style="--score: {score.final_score};">{score.final_score:g}</div>
                <div>
                    <div class="candidate-name">{score.skill_match_score:g}%</div>
                    <div class="mini-meter"><span style="width: {score.skill_match_score}%;"></span></div>
                </div>
                <div>
                    <div class="candidate-name">{score.experience_score:g}%</div>
                    <div class="mini-meter"><span style="width: {score.experience_score}%;"></span></div>
                </div>
                <div class="candidate-meta">{escape(score.recommendation)}</div>
                <div><span class="status-badge {klass}">{label}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def radar_chart(score) -> go.Figure:
    categories = ["Similarity", "Skills", "Experience", "Education"]
    values = [
        score.similarity_score,
        score.skill_match_score,
        score.experience_score,
        score.education_score,
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + values[:1],
            theta=categories + categories[:1],
            fill="toself",
            name=score.candidate,
            line={"color": "#7C3AED"},
            fillcolor="rgba(124,58,237,0.22)",
        )
    )
    fig.update_layout(
        polar={
            "radialaxis": {"visible": True, "range": [0, 100], "gridcolor": "rgba(255,255,255,0.10)"},
            "angularaxis": {"gridcolor": "rgba(255,255,255,0.10)"},
            "bgcolor": "rgba(17,24,39,0.20)",
        },
        showlegend=False,
    )
    return style_plotly(fig)


def skill_comparison_chart(score) -> go.Figure:
    found = len(score.skills_found)
    missing = len(score.missing_skills)
    fig = px.bar(
        x=["Matched Skills", "Missing Skills"],
        y=[found, missing],
        title="Skill Comparison",
        color=["Matched Skills", "Missing Skills"],
        color_discrete_map={"Matched Skills": "#10B981", "Missing Skills": "#F59E0B"},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Skills")
    return style_plotly(fig)


def funnel_chart(scores) -> go.Figure:
    total = max(len(st.session_state.resumes), len(scores))
    screened = len(scores)
    shortlisted = sum(score.final_score >= 75 for score in scores)
    interview = sum(score.final_score >= 85 for score in scores)
    selected = 1 if interview else 0
    fig = go.Figure(
        go.Funnel(
            y=["Applied", "Screened", "Shortlisted", "Interview", "Selected"],
            x=[total, screened, shortlisted, interview, selected],
            marker={"color": ["#2563EB", "#4F46E5", "#7C3AED", "#10B981", "#F59E0B"]},
            textinfo="value+percent initial",
        )
    )
    fig.update_layout(title="Candidate Funnel")
    return style_plotly(fig)


def page_dashboard() -> None:
    render_header(
        "AI-Powered Recruitment Intelligence",
        "One command center for screening resumes, ranking candidates, and turning role requirements into hiring decisions.",
    )
    render_kpis()

    scores = st.session_state.scores
    left, right = st.columns([1.05, 0.95])
    with left:
        render_section("Candidate Funnel", "Track candidate movement from application to selection.")
        st.plotly_chart(funnel_chart(scores), use_container_width=True)
    with right:
        render_section("Pipeline Quality")
        if scores:
            df = score_dataframe(scores)
            fig = px.bar(
                df,
                x="candidate",
                y="final_score",
                color="status",
                title="ATS Score Distribution",
                color_discrete_map={
                    "Shortlist": "#10B981",
                    "Review": "#F59E0B",
                    "Reject": "#EF4444",
                },
            )
            st.plotly_chart(style_plotly(fig), use_container_width=True)
        else:
            st.info("Upload a job description and resumes to populate ranking analytics.")

    if scores:
        render_section("Top Ranked Candidates", "Highest scoring applicants based on similarity, skills, experience, and education.")
        render_candidate_rows(scores[:5])


def page_job_descriptions() -> None:
    render_header(
        "Job Description Analyzer",
        "Extract required technologies, experience signals, skills, and keyword intelligence from every role.",
    )
    render_kpis()

    left, right = st.columns([1.15, 0.85])
    with left:
        render_section(
            "Job Description Intake",
            "Drop in a PDF/TXT job description or paste the role requirements.",
        )
        render_upload_visual("Analyze a Job Description", "PDF, TXT, or pasted role requirements", 65 if st.session_state.job_description else 12)
        st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
        upload = st.file_uploader("Upload Job Description", type=["pdf", "txt"])
        st.markdown("</div>", unsafe_allow_html=True)
        pasted = st.text_area("Paste Job Description", height=260)

    with right:
        render_section("Role Intelligence", "Detected skills, technologies, and hiring criteria.")
        if st.session_state.job_description:
            required = extract_skills(st.session_state.job_description)
            st.metric("Required Skills", len(required))
            render_skill_pills(required)
            st.markdown("<br>", unsafe_allow_html=True)
            words = st.session_state.job_description.lower().split()
            keyword_df = (
                pd.Series([word.strip(".,:;()[]") for word in words if len(word) > 3])
                .value_counts()
                .head(10)
                .reset_index()
            )
            if keyword_df.empty:
                st.caption("Add more role detail to generate keyword analysis.")
            else:
                keyword_df.columns = ["Keyword", "Frequency"]
                fig = px.bar(
                    keyword_df,
                    x="Frequency",
                    y="Keyword",
                    orientation="h",
                    title="Keyword Analysis",
                    color="Frequency",
                    color_continuous_scale=["#1E293B", "#2563EB", "#7C3AED"],
                )
                st.plotly_chart(style_plotly(fig), use_container_width=True)
        else:
            st.info("Add a job description to reveal required skills and scoring signals.")

    if upload is not None:
        try:
            if upload.name.lower().endswith(".pdf"):
                st.session_state.job_description = extract_text_from_upload(upload)
            else:
                st.session_state.job_description = read_text_upload(upload)
            st.success("Job description uploaded.")
        except (PDFExtractionError, UnicodeDecodeError) as exc:
            st.error(f"Could not parse job description: {exc}")

    if pasted.strip():
        st.session_state.job_description = pasted


def page_resume_screening() -> None:
    render_header(
        "Resume Screening",
        "Parse resumes, preview files, and run AI-powered matching against the active job description.",
    )
    render_kpis()
    render_section(
        "Premium Resume Upload",
        "Drag and drop multiple PDF/TXT resumes. XtenHire extracts text, detects skills, and prepares ranking.",
    )

    render_upload_visual(
        "Drop Candidate Resumes",
        "Batch upload resumes for screening and shortlist generation",
        min(len(st.session_state.resumes) * 18, 100),
    )
    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
    uploads = st.file_uploader(
        "Upload Multiple Resumes",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploads:
        parsed = {}
        for upload in uploads:
            result = parse_uploaded_resume(upload)
            if result:
                candidate, text = result
                parsed[candidate] = text
        if parsed:
            st.session_state.resumes.update(parsed)
            st.success(f"Loaded {len(parsed)} resume(s).")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Run AI Ranking", type="primary", use_container_width=True):
            run_ranking()
    with col2:
        if st.session_state.scores:
            st.success("Ranking complete. Open Candidate Ranking or Insights.")

    if st.session_state.resumes:
        render_section("File Preview", "Parsed resumes ready for AI screening.")
        preview_cols = st.columns(3)
        for index, (candidate, text) in enumerate(st.session_state.resumes.items()):
            with preview_cols[index % 3]:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div class="section-title">{candidate}</div>
                        <p class="muted">{len(text.split())} words parsed</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Preview resume text"):
                    st.write(text[:1200] + ("..." if len(text) > 1200 else ""))


def page_candidates() -> None:
    render_header(
        "Candidates",
        "Review ranked applicants, match quality, status, and AI-generated hiring recommendations.",
    )
    render_kpis()

    if st.button("Refresh Ranking", type="primary"):
        run_ranking()

    scores = st.session_state.scores
    if not scores:
        st.info("Upload a JD and resumes, then run ranking.")
        return

    df = score_dataframe(scores)
    render_section("Candidate Ranking Table", "Custom ATS ranking rows with score rings, fit meters, and status badges.")
    render_candidate_rows(scores)

    action1, action2, _ = st.columns([1, 1, 3])
    csv = df.to_csv(index=False).encode("utf-8")
    with action1:
        st.download_button(
            "Export CSV",
            csv,
            file_name="xtenhire_candidate_ranking.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with action2:
        st.download_button(
            "Export Report",
            generate_hiring_report(scores),
            file_name="xtenhire_hiring_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    render_section("Candidate Detail Drawer", "Open a candidate profile with radar fit, skill comparison, and recommendation context.")
    selected = st.selectbox("Open Candidate Profile", [score.candidate for score in scores])
    score = next(item for item in scores if item.candidate == selected)
    left, right = st.columns([0.88, 1.12])
    with left:
        label, klass = status_label(score)
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="avatar" style="width: 54px; height: 54px; font-size: 1rem;">{escape(score.candidate[:2].upper())}</div>
                <h3 style="margin: 0.85rem 0 0.15rem;">{escape(score.candidate)}</h3>
                <p class="muted">{score.years_experience:g} years experience | {len(score.skills_found)} matched skills</p>
                <div style="display:flex; align-items:center; gap:1rem; margin-top:1rem;">
                    <div class="score-ring" style="--score:{score.final_score}; width:82px; height:82px; font-size:1rem;">{score.final_score:g}</div>
                    <span class="status-badge {klass}">{label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_section("Matched Skills")
        render_skill_pills(score.skills_found)
        render_section("Missing Skills")
        render_skill_pills(score.missing_skills, empty="No missing skills detected")
        render_section("Recommendation")
        st.info(score.recommendation)
    with right:
        st.plotly_chart(radar_chart(score), use_container_width=True)
        st.plotly_chart(skill_comparison_chart(score), use_container_width=True)


def page_reports() -> None:
    render_header(
        "Reports",
        "Export ranking data and generate hiring summaries for recruiters and hiring managers.",
    )
    render_kpis()

    scores = st.session_state.scores
    if not scores:
        st.info("Run candidate ranking to create reports.")
        return

    df = score_dataframe(scores)
    left, right = st.columns([0.9, 1.1])
    with left:
        render_section("Report Exports", "Download structured rankings or a concise hiring report.")
        st.download_button(
            "Download Candidate CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="xtenhire_candidate_ranking.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "Download Hiring Report",
            generate_hiring_report(scores),
            file_name="xtenhire_hiring_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with right:
        render_section("Executive Summary")
        st.code(generate_hiring_report(scores), language="text")


def page_analytics() -> None:
    render_header(
        "Analytics",
        "Analyze hiring quality, score distribution, top skills, and role-specific talent gaps.",
    )
    render_kpis()

    scores = st.session_state.scores
    if not scores:
        st.info("Run candidate ranking to generate analytics.")
        return

    df = score_dataframe(scores)
    score_chart = px.bar(
        df,
        x="candidate",
        y="final_score",
        color="status",
        title="Candidate Scores",
        labels={"candidate": "Candidate", "final_score": "ATS Score"},
        color_discrete_map={
            "Shortlist": "#10B981",
            "Review": "#F59E0B",
            "Reject": "#EF4444",
        },
    )
    st.plotly_chart(style_plotly(score_chart), use_container_width=True)

    all_skills = []
    missing_skills = []
    for score in scores:
        all_skills.extend(score.skills_found)
        missing_skills.extend(score.missing_skills)

    col1, col2 = st.columns(2)
    if all_skills:
        skills_df = pd.Series(all_skills).value_counts().head(12).reset_index()
        skills_df.columns = ["skill", "count"]
        col1.plotly_chart(
            style_plotly(
                px.bar(
                    skills_df,
                    x="skill",
                    y="count",
                    title="Top Skills",
                    color="count",
                    color_continuous_scale=["#1E293B", "#2563EB", "#7C3AED"],
                )
            ),
            use_container_width=True,
        )
    if missing_skills:
        gap_df = pd.Series(missing_skills).value_counts().head(12).reset_index()
        gap_df.columns = ["skill", "gap_count"]
        col2.plotly_chart(
            style_plotly(
                px.bar(
                    gap_df,
                    x="skill",
                    y="gap_count",
                    title="Skill Gap Analysis",
                    color="gap_count",
                    color_continuous_scale=["#1E293B", "#F59E0B", "#7C3AED"],
                )
            ),
            use_container_width=True,
        )

    component_df = df[
        [
            "candidate",
            "similarity_score",
            "skill_match_score",
            "experience_score",
            "education_score",
        ]
    ].melt(id_vars="candidate", var_name="component", value_name="score")
    st.plotly_chart(
        style_plotly(
            px.bar(
                component_df,
                x="candidate",
                y="score",
                color="component",
                barmode="group",
                title="Score Component Breakdown",
                color_discrete_sequence=["#2563EB", "#7C3AED", "#10B981", "#F59E0B"],
            )
        ),
        use_container_width=True,
    )


def page_settings() -> None:
    render_header(
        "Settings",
        "Configure scoring weights and product preferences for the XtenHire AI workspace.",
    )
    render_section("Workspace Configuration", "Authentication, database, multi-user support, and collaboration are intentionally skipped for this version.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Similarity Weight", "50%")
    col2.metric("Skill Weight", "25%")
    col3.metric("Experience Weight", "15%")
    col4.metric("Education Weight", "10%")


def main() -> None:
    init_state()
    apply_custom_css()
    page = render_sidebar()
    render_topbar()

    pages = {
        "Dashboard": page_dashboard,
        "Candidates": page_candidates,
        "Resume Screening": page_resume_screening,
        "Job Descriptions": page_job_descriptions,
        "Analytics": page_analytics,
        "Reports": page_reports,
        "Settings": page_settings,
    }
    pages[page]()


if __name__ == "__main__":
    main()
