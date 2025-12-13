"""
Модуль для оценки качества RAG системы.

Включает все метрики:
- Retrieval: Context Precision, Context Recall, Context Relevancy
- Generation: Faithfulness, Answer Relevancy, Answer Semantic Similarity
- LLM-as-a-judge для кастомной оценки
"""

from .metrics import (
    get_metrics_for_retrieval_only,
    get_metrics_for_full_pipeline_no_gt,
    get_metrics_for_full_pipeline_with_gt,
    get_custom_metrics_real_estate,
)
from .evaluator import RAGEvaluator

__all__ = [
    "get_metrics_for_retrieval_only",
    "get_metrics_for_full_pipeline_no_gt",
    "get_metrics_for_full_pipeline_with_gt",
    "get_custom_metrics_real_estate",
    "RAGEvaluator",
]
