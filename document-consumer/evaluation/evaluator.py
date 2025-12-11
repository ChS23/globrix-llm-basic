"""
RAG Evaluator - оркестратор для оценки качества RAG системы.

Основной класс RAGEvaluator умеет:
1. Загружать тестовый датасет
2. Запускать retrieval через vector store
3. Запускать generation
4. Оценивать качество с помощью метрик DeepEval
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from deepeval.test_case import LLMTestCase
from deepeval import evaluate
import structlog

from app.vector_store.store import DocumentVectorStore
from app.config.settings import Settings


logger = structlog.get_logger(__name__)


class RAGEvaluator:
    """
    Evaluator для оценки качества RAG системы.

    Умеет запускать оценку на разных этапах:
    - Только retrieval (без generation)
    - Полный pipeline (retrieval + generation)
    - С ground truth или без

    Attributes:
        dataset_path: Путь к JSON файлу с тестовыми данными
        dataset: Загруженный датасет (list of dict)
        settings: Настройки приложения
    """

    def __init__(self, dataset_path: str):
        """
        Инициализация evaluator.

        Args:
            dataset_path: Путь к файлу с тестовыми данными (JSON)

        Example:
            >>> evaluator = RAGEvaluator("evaluation/test_dataset.json")
        """
        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()
        self.settings = Settings()

        logger.info(
            "RAGEvaluator initialized",
            dataset_path=str(self.dataset_path),
            dataset_size=len(self.dataset),
        )

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """
        Загружает тестовый датасет из JSON файла.

        Returns:
            List словарей с полями:
            - question: str - вопрос пользователя
            - contexts: list[list[str]] - релевантные контексты (опционально)
            - answer: str - ожидаемый ответ (опционально)
            - ground_truth: str - эталонный ответ для метрик с GT

        Raises:
            FileNotFoundError: Если файл датасета не найден
            json.JSONDecodeError: Если JSON невалидный
        """
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Нормализация: распаковать question и ground_truth если они в списке
        for item in data:
            if isinstance(item.get("question"), list):
                item["question"] = item["question"][0]
            if isinstance(item.get("ground_truth"), list):
                item["ground_truth"] = item["ground_truth"][0]
            # contexts оставляем как есть - это список списков для DeepEval

        logger.info("Dataset loaded", items_count=len(data))
        return data

    async def run_retrieval(self, question: str, k: int = 5) -> List[str]:
        """
        Запускает retrieval для вопроса через vector store.

        Args:
            question: Вопрос пользователя
            k: Количество документов для извлечения (top-k)

        Returns:
            List строк - содержимое найденных документов (chunks)

        Example:
            >>> contexts = await evaluator.run_retrieval(
            ...     "Какие квартиры в Лиссабоне?",
            ...     k=5
            ... )
            >>> print(f"Found {len(contexts)} relevant chunks")
        """
        logger.debug("Running retrieval", question=question, k=k)

        # Получить singleton instance vector store
        store = DocumentVectorStore.get_instance()

        # Поиск документов
        docs = await store.search(query=question, k=k)

        # Извлечь текст из Document объектов
        contexts = [doc.page_content for doc in docs]

        logger.debug(
            "Retrieval completed",
            question=question,
            retrieved_count=len(contexts),
        )

        return contexts

    async def run_generation(
        self, question: str, contexts: List[str]
    ) -> str:
        """
        Запускает generation для создания ответа.

        ВАЖНО: Пока это заглушка!
        TODO: Заменить на вызов regional_rag_tool когда будет готов.

        Args:
            question: Вопрос пользователя
            contexts: List контекстов из retrieval

        Returns:
            str - сгенерированный ответ

        Example:
            >>> answer = await evaluator.run_generation(
            ...     question="Какие квартиры?",
            ...     contexts=["В Лиссабоне есть...", "Цены на..."]
            ... )
        """
        logger.warning(
            "Using MOCK generation (regional_rag_tool not implemented yet)",
            question=question,
            contexts_count=len(contexts),
        )

        # TODO: Заменить на реальный вызов
        # from agent_orchestrator.tools import regional_rag_tool
        # answer = await regional_rag_tool(question=question, contexts=contexts)

        # Заглушка для тестирования структуры
        mock_answer = (
            f"Mock answer based on {len(contexts)} contexts. "
            f"Question: {question[:50]}..."
        )

        return mock_answer

    async def evaluate_retrieval_only(
        self, metrics: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Оценка только retrieval (БЕЗ generation).

        Метрики по умолчанию:
        - Context Precision (ранжирование)
        - Context Relevancy (релевантность)

        Args:
            metrics: List метрик для оценки (если None - используются по умолчанию)

        Returns:
            Dict с результатами оценки:
            - metric_name: score (float)
            - test_cases: list использованных тест-кейсов

        Example:
            >>> results = await evaluator.evaluate_retrieval_only()
            >>> print(f"Context Precision: {results['contextual_precision']:.3f}")
        """
        from .metrics import get_metrics_for_retrieval_only

        if metrics is None:
            metrics = get_metrics_for_retrieval_only()

        logger.info(
            "Starting RETRIEVAL-ONLY evaluation",
            dataset_size=len(self.dataset),
            metrics_count=len(metrics),
        )

        test_cases = []

        for idx, item in enumerate(self.dataset):
            question = item["question"]
            ground_truth = item.get("ground_truth", "")

            logger.debug(
                f"Processing item {idx + 1}/{len(self.dataset)}",
                question=question[:50],
            )

            # Запустить retrieval
            contexts = await self.run_retrieval(question)

            # Создать test case БЕЗ actual_output (для retrieval метрик)
            test_case = LLMTestCase(
                input=question,
                retrieval_context=contexts,
                expected_output=ground_truth,  # Нужен для Context Precision
            )
            test_cases.append(test_case)

        # Запустить оценку через DeepEval
        logger.info(
            "Running DeepEval evaluation",
            test_cases_count=len(test_cases),
        )

        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_full_pipeline_no_gt(
        self, metrics: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Полная оценка retrieval + generation БЕЗ ground truth.

        Метрики по умолчанию:
        - Context Precision, Context Relevancy (retrieval)
        - Faithfulness, Answer Relevancy (generation)

        Args:
            metrics: List метрик (если None - используются по умолчанию)

        Returns:
            Dict с результатами всех метрик

        Example:
            >>> results = await evaluator.evaluate_full_pipeline_no_gt()
            >>> print(f"Faithfulness: {results['faithfulness']:.3f}")
        """
        from .metrics import get_metrics_for_full_pipeline_no_gt

        if metrics is None:
            metrics = get_metrics_for_full_pipeline_no_gt()

        logger.info(
            "Starting FULL PIPELINE (no GT) evaluation",
            dataset_size=len(self.dataset),
            metrics_count=len(metrics),
        )

        test_cases = []

        for idx, item in enumerate(self.dataset):
            question = item["question"]

            logger.debug(
                f"Processing item {idx + 1}/{len(self.dataset)}",
                question=question[:50],
            )

            # 1. Retrieval
            contexts = await self.run_retrieval(question)

            # 2. Generation
            answer = await self.run_generation(question, contexts)

            # 3. Создать test case С actual_output
            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=contexts,
            )
            test_cases.append(test_case)

        # Оценка
        logger.info("Running DeepEval evaluation", test_cases_count=len(test_cases))
        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_full_pipeline_with_gt(
        self, metrics: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Полная оценка retrieval + generation С ground truth.

        Метрики:
        - ВСЕ retrieval метрики (включая Context Recall)
        - ВСЕ generation метрики (включая Semantic Similarity)

        Args:
            metrics: List метрик (если None - все доступные метрики)

        Returns:
            Dict с результатами всех метрик

        Example:
            >>> results = await evaluator.evaluate_full_pipeline_with_gt()
            >>> print(f"Context Recall: {results['contextual_recall']:.3f}")
            >>> print(f"Semantic Similarity: {results['semantic_similarity']:.3f}")
        """
        from .metrics import get_metrics_for_full_pipeline_with_gt

        if metrics is None:
            metrics = get_metrics_for_full_pipeline_with_gt()

        logger.info(
            "Starting FULL PIPELINE (with GT) evaluation",
            dataset_size=len(self.dataset),
            metrics_count=len(metrics),
        )

        test_cases = []

        for idx, item in enumerate(self.dataset):
            question = item["question"]
            ground_truth = item.get("ground_truth", "")

            if not ground_truth:
                logger.warning(
                    f"Item {idx + 1} missing ground_truth, skipping",
                    question=question[:50],
                )
                continue

            logger.debug(
                f"Processing item {idx + 1}/{len(self.dataset)}",
                question=question[:50],
            )

            # 1. Retrieval
            contexts = await self.run_retrieval(question)

            # 2. Generation
            answer = await self.run_generation(question, contexts)

            # 3. Test case С ground truth
            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=contexts,
                expected_output=ground_truth,
            )
            test_cases.append(test_case)

        if not test_cases:
            raise ValueError("No test cases with ground_truth found in dataset!")

        # Оценка
        logger.info("Running DeepEval evaluation", test_cases_count=len(test_cases))
        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_custom(
        self, metrics: List, include_generation: bool = True
    ) -> Dict[str, Any]:
        """
        Оценка с кастомными метриками (включая LLM-as-a-judge).

        Args:
            metrics: List кастомных метрик для оценки
            include_generation: Запускать ли generation (если False - только retrieval)

        Returns:
            Dict с результатами кастомных метрик

        Example:
            >>> from evaluation.metrics import CUSTOM_METRICS_REAL_ESTATE
            >>> results = await evaluator.evaluate_custom(
            ...     metrics=CUSTOM_METRICS_REAL_ESTATE,
            ...     include_generation=True
            ... )
        """
        logger.info(
            "Starting CUSTOM evaluation",
            metrics_count=len(metrics),
            include_generation=include_generation,
        )

        test_cases = []

        for idx, item in enumerate(self.dataset):
            question = item["question"]
            ground_truth = item.get("ground_truth", "")

            # Retrieval
            contexts = await self.run_retrieval(question)

            # Generation (если нужен)
            if include_generation:
                answer = await self.run_generation(question, contexts)
                test_case = LLMTestCase(
                    input=question,
                    actual_output=answer,
                    retrieval_context=contexts,
                    expected_output=ground_truth,
                )
            else:
                test_case = LLMTestCase(
                    input=question,
                    retrieval_context=contexts,
                    expected_output=ground_truth,
                )

            test_cases.append(test_case)

        # Оценка
        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Custom evaluation completed", results=results)
        return results