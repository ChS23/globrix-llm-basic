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
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
import structlog

from app.vector_store.store import get_vector_store
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
        store = get_vector_store()

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
        Запускает generation для создания ответа через agent-orchestrator.

        Вызывает HTTP endpoint agent-orchestrator для получения ответа.

        Args:
            question: Вопрос пользователя
            contexts: List контекстов из retrieval

        Returns:
            str - сгенерированный ответ

        Raises:
            RuntimeError: Если agent-orchestrator недоступен

        Example:
            >>> answer = await evaluator.run_generation(
            ...     question="Какие квартиры?",
            ...     contexts=["В Лиссабоне есть...", "Цены на..."]
            ... )
        """
        agent_url = os.getenv("AGENT_ORCHESTRATOR_URL", "http://localhost:8000")

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Формируем запрос с контекстом
            context_text = "\n\n".join(contexts)
            augmented_question = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {question}"""

            response = await client.post(
                f"{agent_url}/chat",
                json={
                    "message": augmented_question,
                    "thread_id": f"eval-{hash(question) % 10000}",
                },
            )
            response.raise_for_status()

            data = response.json()
            answer = data.get("response", "")

            logger.debug(
                "Generation completed via agent-orchestrator",
                question=question[:50],
                answer_length=len(answer),
            )

            return answer

    async def _process_item_retrieval(
        self, idx: int, item: Dict[str, Any]
    ) -> LLMTestCase:
        """
        Обрабатывает один элемент датасета для retrieval-only оценки.
        """
        question = item["question"]
        ground_truth = item.get("ground_truth", "")

        logger.debug(
            f"Processing item {idx + 1}",
            question=question[:50],
        )

        contexts = await self.run_retrieval(question)

        return LLMTestCase(
            input=question,
            retrieval_context=contexts,
            expected_output=ground_truth,
        )

    async def _process_item_full(
        self, idx: int, item: Dict[str, Any], include_gt: bool = False
    ) -> Optional[LLMTestCase]:
        """
        Обрабатывает один элемент датасета для full pipeline оценки.
        """
        question = item["question"]
        ground_truth = item.get("ground_truth", "")

        if include_gt and not ground_truth:
            logger.warning(
                f"Item {idx + 1} missing ground_truth, skipping",
                question=question[:50],
            )
            return None

        logger.debug(
            f"Processing item {idx + 1}",
            question=question[:50],
        )

        # 1. Retrieval
        contexts = await self.run_retrieval(question)

        # 2. Generation
        answer = await self.run_generation(question, contexts)

        # 3. Test case
        if include_gt:
            return LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=contexts,
                expected_output=ground_truth,
            )
        else:
            return LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=contexts,
            )

    async def evaluate_retrieval_only(
        self, metrics: Optional[List] = None, max_concurrency: int = 3
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
            max_concurrency=max_concurrency,
        )

        # Параллельная обработка с ограничением concurrency
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_with_semaphore(idx: int, item: Dict[str, Any]) -> LLMTestCase:
            async with semaphore:
                return await self._process_item_retrieval(idx, item)

        tasks = [
            process_with_semaphore(idx, item)
            for idx, item in enumerate(self.dataset)
        ]

        test_cases = await asyncio.gather(*tasks)

        # Запустить оценку через DeepEval
        logger.info(
            "Running DeepEval evaluation",
            test_cases_count=len(test_cases),
        )

        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_full_pipeline_no_gt(
        self, metrics: Optional[List] = None, max_concurrency: int = 3
    ) -> Dict[str, Any]:
        """
        Полная оценка retrieval + generation БЕЗ ground truth.

        Метрики по умолчанию:
        - Context Precision, Context Relevancy (retrieval)
        - Faithfulness, Answer Relevancy (generation)

        Args:
            metrics: List метрик (если None - используются по умолчанию)
            max_concurrency: Максимальное количество параллельных запросов

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
            max_concurrency=max_concurrency,
        )

        # Параллельная обработка с ограничением concurrency
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_with_semaphore(idx: int, item: Dict[str, Any]) -> Optional[LLMTestCase]:
            async with semaphore:
                return await self._process_item_full(idx, item, include_gt=False)

        tasks = [
            process_with_semaphore(idx, item)
            for idx, item in enumerate(self.dataset)
        ]

        test_cases = [tc for tc in await asyncio.gather(*tasks) if tc is not None]

        # Оценка
        logger.info("Running DeepEval evaluation", test_cases_count=len(test_cases))
        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_full_pipeline_with_gt(
        self, metrics: Optional[List] = None, max_concurrency: int = 3
    ) -> Dict[str, Any]:
        """
        Полная оценка retrieval + generation С ground truth.

        Метрики:
        - ВСЕ retrieval метрики (включая Context Recall)
        - ВСЕ generation метрики (включая Semantic Similarity)

        Args:
            metrics: List метрик (если None - все доступные метрики)
            max_concurrency: Максимальное количество параллельных запросов

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
            max_concurrency=max_concurrency,
        )

        # Параллельная обработка с ограничением concurrency
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_with_semaphore(idx: int, item: Dict[str, Any]) -> Optional[LLMTestCase]:
            async with semaphore:
                return await self._process_item_full(idx, item, include_gt=True)

        tasks = [
            process_with_semaphore(idx, item)
            for idx, item in enumerate(self.dataset)
        ]

        test_cases = [tc for tc in await asyncio.gather(*tasks) if tc is not None]

        if not test_cases:
            raise ValueError("No test cases with ground_truth found in dataset!")

        # Оценка
        logger.info("Running DeepEval evaluation", test_cases_count=len(test_cases))
        results = evaluate(test_cases=test_cases, metrics=metrics)

        logger.info("Evaluation completed", results=results)
        return results

    async def evaluate_custom(
        self, metrics: List, include_generation: bool = True, max_concurrency: int = 3
    ) -> Dict[str, Any]:
        """
        Оценка с кастомными метриками (включая LLM-as-a-judge).

        Args:
            metrics: List кастомных метрик для оценки
            include_generation: Запускать ли generation (если False - только retrieval)
            max_concurrency: Максимальное количество параллельных запросов

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
            max_concurrency=max_concurrency,
        )

        # Параллельная обработка
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_item(idx: int, item: Dict[str, Any]) -> LLMTestCase:
            async with semaphore:
                question = item["question"]
                ground_truth = item.get("ground_truth", "")

                logger.debug(f"Processing item {idx + 1}", question=question[:50])

                contexts = await self.run_retrieval(question)

                if include_generation:
                    answer = await self.run_generation(question, contexts)
                    return LLMTestCase(
                        input=question,
                        actual_output=answer,
                        retrieval_context=contexts,
                        expected_output=ground_truth,
                    )
                else:
                    return LLMTestCase(
                        input=question,
                        retrieval_context=contexts,
                        expected_output=ground_truth,
                    )

        tasks = [process_item(idx, item) for idx, item in enumerate(self.dataset)]
        test_cases = await asyncio.gather(*tasks)

        # Оценка
        results = evaluate(test_cases=list(test_cases), metrics=metrics)

        logger.info("Custom evaluation completed", results=results)
        return results