"""
CLI скрипт для запуска оценки RAG системы.

Использование:
    # Только retrieval (без generation)
    python -m evaluation.run_evaluation --mode retrieval

    # Полный pipeline без GT
    python -m evaluation.run_evaluation --mode full-no-gt

    # Полный pipeline с GT
    python -m evaluation.run_evaluation --mode full-with-gt

    # Кастомные метрики
    python -m evaluation.run_evaluation --mode custom

    # Указать свой датасет
    python -m evaluation.run_evaluation \
        --dataset evaluation/my_dataset.json \
        --mode retrieval
"""

import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime
import sys

import structlog

from .evaluator import RAGEvaluator
from .metrics import CUSTOM_METRICS_REAL_ESTATE


logger = structlog.get_logger(__name__)


def print_results(results: dict, mode: str):
    """
    Печатает результаты оценки в консоль.

    Args:
        results: Dict с результатами от evaluate()
        mode: Режим оценки (для контекста)
    """
    print("\n" + "=" * 70)
    print(f"📊 EVALUATION RESULTS - {mode.upper()}")
    print("=" * 70)

    # Распечатать метрики
    for key, value in results.items():
        if isinstance(value, (int, float)):
            # Определить статус на основе порога
            if value >= 0.9:
                status = "✅ EXCELLENT"
            elif value >= 0.8:
                status = "✅ GOOD"
            elif value >= 0.7:
                status = "⚠️  ACCEPTABLE"
            else:
                status = "❌ NEEDS IMPROVEMENT"

            print(f"{status:<20} {key:<30} {value:.3f}")

    print("=" * 70)


def save_results(results: dict, output_path: Path, mode: str, dataset_path: Path):
    """
    Сохраняет результаты в JSON файл с метаданными.

    Args:
        results: Dict с результатами
        output_path: Путь для сохранения
        mode: Режим оценки
        dataset_path: Путь к использованному датасету
    """
    # Добавить метаданные
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "dataset": str(dataset_path),
        "results": results,
    }

    # Создать директорию если нужно
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Сохранить
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_path}")


async def run_retrieval_mode(evaluator: RAGEvaluator) -> dict:
    """
    Запуск оценки только retrieval.

    Args:
        evaluator: Инициализированный RAGEvaluator

    Returns:
        Dict с результатами оценки
    """
    print("\n🔍 Running RETRIEVAL-ONLY evaluation...")
    print("Metrics: Context Precision, Context Relevancy")
    print("-" * 70)

    results = await evaluator.evaluate_retrieval_only()
    return results


async def run_full_no_gt_mode(evaluator: RAGEvaluator) -> dict:
    """
    Запуск полной оценки БЕЗ ground truth.

    Args:
        evaluator: Инициализированный RAGEvaluator

    Returns:
        Dict с результатами оценки
    """
    print("\n🚀 Running FULL PIPELINE (no GT) evaluation...")
    print("Metrics: Context Precision, Context Relevancy, Faithfulness, Answer Relevancy")
    print("-" * 70)

    results = await evaluator.evaluate_full_pipeline_no_gt()
    return results


async def run_full_with_gt_mode(evaluator: RAGEvaluator) -> dict:
    """
    Запуск полной оценки С ground truth.

    Args:
        evaluator: Инициализированный RAGEvaluator

    Returns:
        Dict с результатами оценки
    """
    print("\n🎯 Running FULL PIPELINE (with GT) evaluation...")
    print("Metrics: ALL (Context Recall, Semantic Similarity included)")
    print("-" * 70)

    results = await evaluator.evaluate_full_pipeline_with_gt()
    return results


async def run_custom_mode(evaluator: RAGEvaluator) -> dict:
    """
    Запуск оценки с кастомными метриками (LLM-as-a-judge).

    Args:
        evaluator: Инициализированный RAGEvaluator

    Returns:
        Dict с результатами оценки
    """
    print("\n⚖️  Running CUSTOM (LLM-as-a-judge) evaluation...")
    print("Metrics: Property Info Completeness, Legal Accuracy")
    print("-" * 70)

    results = await evaluator.evaluate_custom(
        metrics=CUSTOM_METRICS_REAL_ESTATE,
        include_generation=True,
    )
    return results


async def main():
    """
    Главная функция CLI.

    Парсит аргументы и запускает выбранный режим оценки.
    """
    parser = argparse.ArgumentParser(
        description="Evaluate RAG system quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Retrieval only (no generation needed)
  python -m evaluation.run_evaluation --mode retrieval

  # Full pipeline without ground truth
  python -m evaluation.run_evaluation --mode full-no-gt

  # Full pipeline with ground truth
  python -m evaluation.run_evaluation --mode full-with-gt

  # Custom dataset
  python -m evaluation.run_evaluation \
      --dataset evaluation/custom_dataset.json \
      --mode retrieval \
      --output evaluation/custom_results.json
        """,
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="evaluation/test_dataset_gemini.json",
        help="Path to test dataset JSON file (default: evaluation/test_dataset_gemini.json)",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["retrieval", "full-no-gt", "full-with-gt", "custom"],
        default="retrieval",
        help=(
            "Evaluation mode:\n"
            "  retrieval     - Only retrieval metrics (no generation)\n"
            "  full-no-gt    - Full pipeline without ground truth\n"
            "  full-with-gt  - Full pipeline with ground truth\n"
            "  custom        - Custom LLM-as-a-judge metrics"
        ),
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save results JSON (default: evaluation/results_{mode}_{timestamp}.json)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Настроить логирование
    if args.verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
        )

    # Проверить датасет
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset not found: {dataset_path}", file=sys.stderr)
        print(f"   Please create the dataset file first.", file=sys.stderr)
        sys.exit(1)

    # Определить output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"evaluation/results_{args.mode}_{timestamp}.json")

    print("=" * 70)
    print("🧪 RAG EVALUATION TOOL")
    print("=" * 70)
    print(f"Dataset:       {dataset_path}")
    print(f"Mode:          {args.mode}")
    print(f"Output:        {output_path}")
    print("=" * 70)

    try:
        # Создать evaluator
        evaluator = RAGEvaluator(str(dataset_path))

        # Запустить выбранный режим
        if args.mode == "retrieval":
            results = await run_retrieval_mode(evaluator)
        elif args.mode == "full-no-gt":
            results = await run_full_no_gt_mode(evaluator)
        elif args.mode == "full-with-gt":
            results = await run_full_with_gt_mode(evaluator)
        elif args.mode == "custom":
            results = await run_custom_mode(evaluator)
        else:
            print(f"❌ Unknown mode: {args.mode}", file=sys.stderr)
            sys.exit(1)

        # Показать результаты
        print_results(results, args.mode)

        # Сохранить результаты
        save_results(results, output_path, args.mode, dataset_path)

        print("\n✅ Evaluation completed successfully!")

    except Exception as e:
        logger.exception("Evaluation failed", error=str(e))
        print(f"\n❌ Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())