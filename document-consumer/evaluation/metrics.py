"""
Определение всех метрик для оценки RAG системы.

Метрики разделены на 4 группы:
1. RETRIEVAL без GT - Context Precision, Context Relevancy
2. RETRIEVAL с GT - Context Recall
3. GENERATION без GT - Faithfulness, Answer Relevancy
4. GENERATION с GT - Answer Semantic Similarity

Все параметры (модель, пороги) загружаются из .env через Settings.
"""

from deepeval.metrics.ragas import (
    # RAGAS метрики из библиотеки ragas
    RAGASContextualPrecisionMetric,      # Точность ранжирования документов
    RAGASContextualRecallMetric,         # Полнота извлечения (требует GT)
    RAGASFaithfulnessMetric,             # Верность контексту (без галлюцинаций)
    RAGASAnswerRelevancyMetric,          # Релевантность ответа вопросу
)
from deepeval.metrics import (
    ContextualRelevancyMetric,           # Релевантность контекста (DeepEval)
    GEval,                               # LLM-as-a-judge
)
from deepeval.test_case import LLMTestCaseParams

from app.config.settings import Settings


# Загрузить настройки из .env
_settings = Settings()


# ============================================================================
# RETRIEVAL МЕТРИКИ БЕЗ GROUND TRUTH
# ============================================================================

METRICS_RETRIEVAL_NO_GT = [
    RAGASContextualPrecisionMetric(
        threshold=_settings.eval_threshold_context_precision,
        model=_settings.evaluation_model,
    ),
    ContextualRelevancyMetric(
        threshold=_settings.eval_threshold_context_relevancy,
        model=_settings.evaluation_model,
    ),
]


# ============================================================================
# RETRIEVAL МЕТРИКИ С GROUND TRUTH
# ============================================================================

METRICS_RETRIEVAL_WITH_GT = [
    RAGASContextualRecallMetric(
        threshold=_settings.eval_threshold_context_recall,
        model=_settings.evaluation_model,
    ),
]


# ============================================================================
# GENERATION МЕТРИКИ БЕЗ GROUND TRUTH
# ============================================================================

METRICS_GENERATION_NO_GT = [
    RAGASFaithfulnessMetric(
        threshold=_settings.eval_threshold_faithfulness,
        model=_settings.evaluation_model,
    ),
    RAGASAnswerRelevancyMetric(
        threshold=_settings.eval_threshold_answer_relevancy,
        model=_settings.evaluation_model,
    ),
]


# ============================================================================
# GENERATION МЕТРИКИ С GROUND TRUTH
# ============================================================================

METRICS_GENERATION_WITH_GT = [
    # Семантическая близость к эталонному ответу
    GEval(
        name="Answer Semantic Similarity",
        criteria="Determine whether the actual output is semantically similar to the expected output",
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=_settings.eval_threshold_semantic_similarity,
        model=_settings.evaluation_model,
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
    return GEval(
        name=name,
        criteria=criteria,
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=threshold,
        model=_settings.evaluation_model,
    )


# Кастомные метрики для недвижимости
CUSTOM_METRICS_REAL_ESTATE = [
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
            "and up-to-date for Portuguese real estate?"
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

    # Наличие контактной информации
    create_custom_judge_metric(
        name="Contact Information",
        criteria=(
            "Does the answer provide contact information for follow-up "
            "(agent name, phone, email)?"
        ),
        threshold=0.8,
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


# ============================================================================
# ГОТОВЫЕ НАБОРЫ МЕТРИК ДЛЯ РАЗНЫХ СЦЕНАРИЕВ
# ============================================================================

def get_metrics_for_retrieval_only():
    """
    Получить метрики для оценки только retrieval (без generation).

    Использовать когда:
    - Тестируете качество поиска документов

    Returns:
        List метрик, которые не требуют actual_output
    """
    return METRICS_RETRIEVAL_NO_GT


def get_metrics_for_full_pipeline_no_gt():
    """
    Получить все метрики БЕЗ ground truth.

    Использовать когда:
    - Нет эталонных ответов в датасете

    Returns:
        List метрик для retrieval + generation
    """
    return METRICS_RETRIEVAL_NO_GT + METRICS_GENERATION_NO_GT


def get_metrics_for_full_pipeline_with_gt():
    """
    Получить ВСЕ метрики (включая те, что требуют GT).

    Использовать когда:
    - Есть качественные ground truth ответы

    Returns:
        List всех доступных метрик
    """
    return (
        METRICS_RETRIEVAL_NO_GT
        + METRICS_RETRIEVAL_WITH_GT
        + METRICS_GENERATION_NO_GT
        + METRICS_GENERATION_WITH_GT
    )