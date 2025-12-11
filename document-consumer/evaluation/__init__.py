"""
Модуль для оценки качества RAG системы.

Включает все метрики:
- Retrieval: Context Precision, Context Recall, Context Relevancy
- Generation: Faithfulness, Answer Relevancy, Answer Semantic Similarity
- LLM-as-a-judge для кастомной оценки
"""

from .metrics import (
    METRICS_RETRIEVAL_NO_GT,
    METRICS_RETRIEVAL_WITH_GT,
    METRICS_GENERATION_NO_GT,
    METRICS_GENERATION_WITH_GT,
)
from .evaluator import RAGEvaluator

__all__ = [
    "METRICS_RETRIEVAL_NO_GT",
    "METRICS_RETRIEVAL_WITH_GT",
    "METRICS_GENERATION_NO_GT",
    "METRICS_GENERATION_WITH_GT",
    "RAGEvaluator",
]
