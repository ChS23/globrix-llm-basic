"""
Определение всех метрик для оценки RAG системы.

Метрики разделены на 4 группы:
1. RETRIEVAL без GT - Context Precision, Context Relevancy
2. RETRIEVAL с GT - Context Recall
3. GENERATION без GT - Faithfulness, Answer Relevancy
4. GENERATION с GT - Answer Semantic Similarity

Все параметры (модель, пороги) загружаются из .env через Settings.
Метрики создаются лениво при первом обращении.
"""

from typing import List
from functools import lru_cache

from deepeval.metrics import (
    # Native DeepEval метрики (без баговых RAGAS обёрток)
    # RAGAS wrapper в deepeval 3.7.5 имеет баг с capture_metric_type
    ContextualPrecisionMetric,           # Точность ранжирования документов
    ContextualRecallMetric,              # Полнота извлечения (требует GT)
    ContextualRelevancyMetric,           # Релевантность контекста
    FaithfulnessMetric,                  # Верность контексту (без галлюцинаций)
    AnswerRelevancyMetric,               # Релевантность ответа вопросу
    GEval,                               # LLM-as-a-judge
)
from deepeval.test_case import LLMTestCaseParams

from app.config.settings import Settings


@lru_cache(maxsize=1)
def _get_settings() -> Settings:
    """Ленивая загрузка настроек."""
    return Settings()


# ============================================================================
# RETRIEVAL МЕТРИКИ БЕЗ GROUND TRUTH
# ============================================================================

def _get_retrieval_no_gt() -> List:
    """Создаёт метрики для retrieval без GT."""
    settings = _get_settings()
    return [
        ContextualPrecisionMetric(
            threshold=settings.eval_threshold_context_precision,
            model=settings.evaluation_model,
        ),
        ContextualRelevancyMetric(
            threshold=settings.eval_threshold_context_relevancy,
            model=settings.evaluation_model,
        ),
    ]


def _get_retrieval_with_gt() -> List:
    """Создаёт метрики для retrieval с GT."""
    settings = _get_settings()
    return [
        ContextualRecallMetric(
            threshold=settings.eval_threshold_context_recall,
            model=settings.evaluation_model,
        ),
    ]


def _get_generation_no_gt() -> List:
    """Создаёт метрики для generation без GT."""
    settings = _get_settings()
    return [
        FaithfulnessMetric(
            threshold=settings.eval_threshold_faithfulness,
            model=settings.evaluation_model,
        ),
        AnswerRelevancyMetric(
            threshold=settings.eval_threshold_answer_relevancy,
            model=settings.evaluation_model,
        ),
    ]


def _get_generation_with_gt() -> List:
    """Создаёт метрики для generation с GT."""
    settings = _get_settings()
    return [
        GEval(
            name="Answer Semantic Similarity",
            criteria="Determine whether the actual output is semantically similar to the expected output",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            threshold=settings.eval_threshold_semantic_similarity,
            model=settings.evaluation_model,
        ),
    ]




# ============================================================================
# LLM-AS-A-JUDGE КАСТОМНЫЕ МЕТРИКИ
# Дополнительные метрики с промптами для специфичной оценки
# ============================================================================

def create_custom_judge_metric(name: str, criteria: str, threshold: float = 0.8):
    """
    Создает кастомную метрику LLM-as-a-judge.

    Args:
        name: Название метрики (например, "Correctness")
        criteria: Критерий оценки (промпт для LLM судьи)
        threshold: Минимальный проходной балл (0.0 - 1.0)

    Returns:
        GEval метрика для использования в evaluate()

    Пример:
        >>> metric = create_custom_judge_metric(
        ...     name="Politeness",
        ...     criteria="Is the answer polite and professional?",
        ...     threshold=0.9
        ... )
    """
    settings = _get_settings()
    return GEval(
        name=name,
        criteria=criteria,
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        model=settings.evaluation_model,
    )


def _get_custom_metrics_real_estate() -> List:
    """Создаёт кастомные метрики для недвижимости."""
    return [
        # Полнота информации об объекте
        create_custom_judge_metric(
            name="Property Info Completeness",
            criteria=(
                "Does the answer provide complete information about the property "
                "(location, price, size, amenities)?"
            ),
            threshold=0.85,
        ),
        # Юридическая точность
        create_custom_judge_metric(
            name="Legal Accuracy",
            criteria=(
                "Is the legal information (documents, procedures) accurate "
                "and up-to-date for Thai real estate?"
            ),
            threshold=0.9,
        ),
        # Точность информации о цене
        create_custom_judge_metric(
            name="Price Information Accuracy",
            criteria=(
                "Does the answer provide accurate price information with correct "
                "currency and numbers?"
            ),
            threshold=0.9,
        ),
        # Конкретность локации
        create_custom_judge_metric(
            name="Location Specificity",
            criteria=(
                "Does the answer provide specific location details "
                "(city, district, street)?"
            ),
            threshold=0.85,
        ),
        # Качество инвестиционных советов
        create_custom_judge_metric(
            name="Investment Advice Quality",
            criteria=(
                "Does the answer provide useful investment considerations "
                "(ROI, rental yield, market trends)?"
            ),
            threshold=0.85,
        ),
        # Уместность языка
        create_custom_judge_metric(
            name="Language Appropriateness",
            criteria=(
                "Is the language clear, professional, and appropriate for "
                "real estate context?"
            ),
            threshold=0.9,
        ),
    ]


# Для обратной совместимости - глобальные переменные как функции
def get_custom_metrics_real_estate() -> List:
    """Получить кастомные метрики для недвижимости."""
    return _get_custom_metrics_real_estate()




# ============================================================================
# ГОТОВЫЕ НАБОРЫ МЕТРИК ДЛЯ РАЗНЫХ СЦЕНАРИЕВ
# ============================================================================

def get_metrics_for_retrieval_only() -> List:
    """
    Получить метрики для оценки только retrieval (без generation).

    Использовать когда:
    - Тестируете качество поиска документов

    Returns:
        List метрик, которые не требуют actual_output
    """
    return _get_retrieval_no_gt()


def get_metrics_for_full_pipeline_no_gt() -> List:
    """
    Получить все метрики БЕЗ ground truth.

    Использовать когда:
    - Нет эталонных ответов в датасете

    Returns:
        List метрик для retrieval + generation
    """
    return _get_retrieval_no_gt() + _get_generation_no_gt()


def get_metrics_for_full_pipeline_with_gt() -> List:
    """
    Получить ВСЕ метрики (включая те, что требуют GT).

    Использовать когда:
    - Есть качественные ground truth ответы

    Returns:
        List всех доступных метрик
    """
    return (
        _get_retrieval_no_gt()
        + _get_retrieval_with_gt()
        + _get_generation_no_gt()
        + _get_generation_with_gt()
    )