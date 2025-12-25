# RAG Evaluation - Инструкция по использованию

## Результаты оценки (2025-12-13)

### Retrieval Only (38 тестов, 2 метрики)

| Метрика | Значение | Порог | Статус |
|---------|----------|-------|--------|
| **Contextual Precision** | **89.1%** | 80% | ✅ PASS |
| **Contextual Relevancy** | **29.4%** | 50% | ❌ FAIL |

### Full Pipeline без GT (10 тестов, 4 метрики)

| Метрика | Значение | Порог | Статус |
|---------|----------|-------|--------|
| **Answer Relevancy** | **97.5%** | 85% | ✅ PASS |
| **Faithfulness** | **91.8%** | 90% | ✅ PASS |
| **Contextual Precision** | **86.6%** | 80% | ✅ PASS |
| **Contextual Relevancy** | **31.3%** | 50% | ❌ FAIL |

### Full Pipeline с GT (10 тестов, 6 метрик)

| Метрика | Значение | Порог | Статус |
|---------|----------|-------|--------|
| **Answer Relevancy** | **97.1%** | 85% | ✅ PASS |
| **Contextual Recall** | **97.5%** | 90% | ✅ PASS |
| **Contextual Precision** | **87.9%** | 80% | ✅ PASS |
| **Faithfulness** | **85.0%** | 90% | ❌ FAIL |
| **Semantic Similarity** | **70.3%** | 85% | ❌ FAIL |
| **Contextual Relevancy** | **28.6%** | 50% | ❌ FAIL |

- **Модель оценки:** gpt-4o-mini
- **Модель генерации:** openai/gpt-4.1-mini (через agent-orchestrator)

### Интерпретация результатов

**Answer Relevancy (97%)** - Отлично!
- Ответы точно соответствуют заданным вопросам
- Минимум нерелевантной информации в ответах

**Contextual Recall (97.5%)** - Отлично!
- Система извлекает почти всю необходимую информацию из базы
- Ground truth полностью покрывается retrieved контекстом

**Contextual Precision (86-89%)** - Хорошо
- Релевантные документы находятся вверху результатов поиска
- Ранжирование работает правильно

**Faithfulness (85-92%)** - Хорошо
- Ответы в основном основаны на контексте
- Иногда добавляется информация не из контекста

**Semantic Similarity (70%)** - Средне
- Ответы по смыслу похожи на эталонные, но отличаются в деталях
- Система даёт более развёрнутые ответы чем ground truth

**Contextual Relevancy (29-31%)** - Низкий, но типичный для RAG
- Измеряет долю релевантного контента в retrieved chunks
- При k=5 chunks много "шума" (соседний текст в документе)
- Уменьшен chunk_size с 1000 до 700 для улучшения этой метрики

---

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
# Embeddings (OpenAI напрямую)
EMBEDDING_API_KEY=sk-proj-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# DeepEval LLM-as-judge (OpenAI Direct)
OPENAI_API_KEY=sk-proj-...
EVALUATION_MODEL=gpt-4o-mini

# URL agent-orchestrator для generation
AGENT_ORCHESTRATOR_URL=http://localhost:8000

# Пороги для метрик (0.0 - 1.0)
EVAL_THRESHOLD_CONTEXT_PRECISION=0.8
EVAL_THRESHOLD_CONTEXT_RELEVANCY=0.5
EVAL_THRESHOLD_CONTEXT_RECALL=0.9
EVAL_THRESHOLD_FAITHFULNESS=0.9
EVAL_THRESHOLD_ANSWER_RELEVANCY=0.85
EVAL_THRESHOLD_SEMANTIC_SIMILARITY=0.85
```

**Важно:** Используется прямой OpenAI API для LLM-as-judge (не OpenRouter).

## Использование

### 1. Запуск инфраструктуры

```bash
# Запустить Qdrant + RabbitMQ
cd document-consumer
docker-compose up -d

# Запустить agent-orchestrator (для generation)
cd ../agent-orchestrator
uv run python main.py
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
    "question": "What is Chanote in Thailand?",
    "contexts": [["context1"], ["context2"]],
    "ground_truth": "Chanote is the highest form of land title..."
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

# Запустить оценку (с параллельной обработкой)
results = await evaluator.evaluate_retrieval_only(max_concurrency=5)

# Результаты - EvaluationResult объект
for test_result in results.test_results:
    for metric in test_result.metrics_data:
        print(f"{metric.name}: {metric.score}")
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
    include_generation=True,
    max_concurrency=3
)
```

### Получение готовых метрик

```python
from evaluation.metrics import (
    get_metrics_for_retrieval_only,
    get_metrics_for_full_pipeline_no_gt,
    get_metrics_for_full_pipeline_with_gt,
    get_custom_metrics_real_estate,
)

# Метрики создаются лениво при первом вызове
retrieval_metrics = get_metrics_for_retrieval_only()
custom_metrics = get_custom_metrics_real_estate()
```

## Параллельная обработка

Все методы evaluate_* поддерживают параметр `max_concurrency`:

```python
# Retrieval - можно больше параллельных запросов
results = await evaluator.evaluate_retrieval_only(max_concurrency=10)

# Full pipeline - меньше из-за нагрузки на LLM
results = await evaluator.evaluate_full_pipeline_with_gt(max_concurrency=3)
```

## Generation через Agent-Orchestrator

Generation интегрирован с agent-orchestrator через HTTP:

```python
# evaluator.py автоматически вызывает:
POST http://localhost:8000/chat
{
    "message": "Based on the following context...",
    "thread_id": "eval-1234"
}
```

Убедитесь что agent-orchestrator запущен перед оценкой с generation.

## Результаты

Результаты сохраняются в JSON:

```json
{
  "timestamp": "2025-12-13T00:00:00",
  "mode": "retrieval",
  "dataset": "evaluation/test_dataset_gemini.json",
  "summary": {
    "total_tests": 37,
    "passed": 35,
    "failed": 2
  },
  "average_metrics": {
    "Contextual Precision": 0.85,
    "Contextual Relevancy": 0.92
  },
  "detailed_results": [
    {
      "test_index": 0,
      "input": "What is Chanote...",
      "success": true,
      "metrics": {
        "Contextual Precision": {
          "score": 0.9,
          "success": true,
          "reason": "..."
        }
      }
    }
  ]
}
```

## Troubleshooting

### Ошибка: Dataset not found
```bash
ls -la evaluation/test_dataset_gemini.json
```

### Ошибка: Qdrant connection failed
```bash
docker-compose ps
curl http://localhost:6333/collections
```

### Ошибка: Agent-orchestrator unavailable
```bash
curl http://localhost:8000/health
# Или запустите agent-orchestrator
```

### Ошибка: OpenAI API key
```bash
grep OPENAI_API_KEY .env
```

## Технические детали

### Исправления (2025-12-13)

1. **RAGAS → Native DeepEval метрики**
   - DeepEval 3.7.5 имеет баг совместимости с ragas 0.4.1
   - Переключились на native `ContextualPrecisionMetric`, `ContextualRelevancyMetric`

2. **Разделение API ключей**
   - `EMBEDDING_API_KEY` - для OpenAI embeddings напрямую
   - `OPENAI_API_KEY` - для DeepEval LLM-as-judge
   - Явный `openai_api_base` в vector_store для embeddings

3. **Rate limiting**
   - Уменьшена параллельность до `max_concurrency=3`
   - Решает проблему `APIConnectionError` при большом датасете

### Зависимости

```toml
deepeval = "^3.7.5"
ragas = "^0.4.1"  # Опционально, не используется напрямую
httpx = "^0.27.0"
```

## Дальнейшие шаги

1. ✅ Retrieval метрики готовы
2. ✅ Generation интегрирован с agent-orchestrator
3. ✅ Параллельная обработка
4. ✅ Детальные результаты с summary
5. ✅ Все режимы оценки протестированы (retrieval, full-no-gt, full-with-gt)
6. ✅ 6 метрик работают: Precision, Relevancy, Recall, Faithfulness, Answer Relevancy, Semantic Similarity
7. 🔄 Улучшение chunking стратегии (для повышения Relevancy)
8. 🔄 Снижение порогов или улучшение модели генерации (для Faithfulness/Similarity)
