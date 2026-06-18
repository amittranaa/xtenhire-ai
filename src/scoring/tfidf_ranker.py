"""TF-IDF similarity ranking for JD-to-resume matching."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import VECTORIZER_PATH
from src.preprocessing.text_cleaner import clean_text


@dataclass(frozen=True)
class SimilarityResult:
    name: str
    similarity_score: float


class TfidfRanker:
    """Rank resumes by cosine similarity to a job description."""

    def __init__(self, vectorizer: TfidfVectorizer | None = None):
        self.vectorizer = vectorizer or TfidfVectorizer(
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1,
            sublinear_tf=True,
        )

    def score(self, job_description: str, resumes: dict[str, str]) -> list[SimilarityResult]:
        if not job_description.strip():
            raise ValueError("Job description cannot be empty.")
        if not resumes:
            return []

        documents = [clean_text(job_description), *[clean_text(text) for text in resumes.values()]]
        matrix = self.vectorizer.fit_transform(documents)
        similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        results = [
            SimilarityResult(name=name, similarity_score=round(float(score) * 100, 2))
            for name, score in zip(resumes.keys(), similarities)
        ]
        return sorted(results, key=lambda result: result.similarity_score, reverse=True)

    def save(self) -> None:
        import joblib

        VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
