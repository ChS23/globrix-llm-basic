# RAG Evaluation - Инструкция по использованию

## Что реализовано

Система оценки качества RAG с полным набором метрик:

### Retrieval метрики
- **Context Precision** - точность ранжирования документов (без GT)
- **Context Relevancy** - релевантность контекста вопросу (без GT)
- **Context Recall** - полнота извлечения информации (требует GT)

### Generation метрики
- **Faithfulness** - отсутствие галлюцинаций (без GT)
- **Answer Relevancy** - релевантность ответа вопросу (без GT)
- **Answer Semantic Similarity** - семантическая близость к эталону (требует GT)

### LLM-as-a-Judge
- Кастомные метрики для специфичной оценки
- Примеры для недвижимости: Property Info Completeness, Legal Accuracy

## Структура файлов

```
evaluation/
├── __init__.py                    # Экспорты модуля
├── metrics.py                     # Определение всех метрик
├── evaluator.py                   # RAGEvaluator класс
├── run_evaluation.py              # CLI для запуска
├── test_dataset_gemini.json       # Тестовый датасет
└── README.md                      # Эта инструкция
```

## Конфигурация (.env)

Все параметры настраиваются через `.env`:

```bash
# Модель для LLM-as-a-judge
EVALUATION_MODEL=gpt-4o-mini

# Пороги для метрик (0.0 - 1.0)
EVAL_THRESHOLD_CONTEXT_PRECISION=0.8
EVAL_THRESHOLD_CONTEXT_RELEVANCY=0.9
EVAL_THRESHOLD_CONTEXT_RECALL=0.9
EVAL_THRESHOLD_FAITHFULNESS=0.9
EVAL_THRESHOLD_ANSWER_RELEVANCY=0.85
EVAL_THRESHOLD_SEMANTIC_SIMILARITY=0.85
```

## Использование

### 1. Запуск инфраструктуры

```bash
cd document-consumer
docker-compose up -d  # RabbitMQ + Qdrant
```

### 2. Проверка данных в Qdrant

```bash
# Через UI
http://localhost:6333/dashboard

# Через API
curl http://localhost:6333/collections/globrix_docs
```

### 3. Запуск оценки

#### Только retrieval (без generation)
```bash
uv run python -m evaluation.run_evaluation --mode retrieval
```

#### Полный pipeline без GT
```bash
uv run python -m evaluation.run_evaluation --mode full-no-gt
```

#### Полный pipeline с GT
```bash
uv run python -m evaluation.run_evaluation --mode full-with-gt
```

#### Кастомные метрики (LLM-as-a-judge)
```bash
uv run python -m evaluation.run_evaluation --mode custom
```

#### С указанием датасета и output файла
```bash
uv run python -m evaluation.run_evaluation \
    --dataset evaluation/my_dataset.json \
    --mode retrieval \
    --output evaluation/my_results.json
```

## Формат датасета

```json
[
  {
    "question": "Какие квартиры доступны в Лиссабоне?",
    "contexts": [["context1"], ["context2"]],
    "ground_truth": "В Лиссабоне доступны..."
  }
]
```

**Примечание:**
- `question` и `ground_truth` - строки
- `contexts` - список списков строк (формат DeepEval)
- Скрипт автоматически нормализует формат

## Интеграция в код

### Использование в Python

```python
from evaluation import RAGEvaluator

# Создать evaluator
evaluator = RAGEvaluator("evaluation/test_dataset.json")

# Запустить оценку
results = await evaluator.evaluate_retrieval_only()

# Результаты
print(results)
# {
#   "contextual_precision": 0.85,
#   "contextual_relevancy": 0.92
# }
```

### Создание кастомных метрик

```python
from evaluation.metrics import create_custom_judge_metric

metric = create_custom_judge_metric(
    name="Politeness",
    criteria="Is the answer polite and professional?",
    threshold=0.9
)

results = await evaluator.evaluate_custom(
    metrics=[metric],
    include_generation=True
)
```

## Когда generation будет готов

В файле `evaluation/evaluator.py` замените заглушку:

```python
async def run_generation(self, question: str, contexts: List[str]) -> str:
    # TODO: Заменить на реальный вызов
    from agent_orchestrator.tools import regional_rag_tool
    answer = await regional_rag_tool(question=question, contexts=contexts)
    return answer
```

Затем запускайте полную оценку:
```bash
uv run python -m evaluation.run_evaluation --mode full-with-gt
```

## Изменение настроек

### Изменить модель для оценки
В `.env`:
```bash
EVALUATION_MODEL=gpt-4o  # или claude-3-5-sonnet
```

### Изменить пороги
В `.env`:
```bash
EVAL_THRESHOLD_FAITHFULNESS=0.95  # строже
```

### Добавить новую метрику

В `evaluation/metrics.py`:
```python
CUSTOM_METRICS_REAL_ESTATE.append(
    create_custom_judge_metric(
        name="Tone",
        criteria="Is the tone appropriate for the context?",
        threshold=0.8
    )
)
```

## Результаты

Результаты сохраняются в JSON:

```json
{
  "timestamp": "2025-12-12T00:00:00",
  "mode": "retrieval",
  "dataset": "evaluation/test_dataset_gemini.json",
  "results": {
    "contextual_precision": 0.85,
    "contextual_relevancy": 0.92
  }
}
```

## Troubleshooting

### Ошибка: Dataset not found
Убедитесь что путь к датасету правильный:
```bash
ls -la evaluation/test_dataset_gemini.json
```

### Ошибка: Qdrant connection failed
Проверьте что Qdrant запущен:
```bash
docker-compose ps
curl http://localhost:6333/collections
```

### Ошибка: OpenAI API key
Проверьте `.env`:
```bash
grep EMBEDDING_API_KEY .env
```

## Дальнейшие шаги

1. ✅ Retrieval метрики готовы - можно запускать сейчас
2. ⏳ Когда generation готов - добавить в `evaluator.py`