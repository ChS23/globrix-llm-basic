# Qdrant — Векторная база данных

Qdrant используется в Globrix для хранения эмбеддингов документов и обеспечения семантического поиска в RAG pipeline.

---

## 1. Обзор архитектуры

```
PDF документы → Document Consumer → Qdrant
                      ↓
              (chunking + embeddings)
                      ↓
Agent Orchestrator → Qdrant → RAG Retrieval
```

### Роль Qdrant в системе

| Компонент | Взаимодействие с Qdrant |
|-----------|-------------------------|
| **Document Consumer** | Записывает chunks документов с эмбеддингами |
| **Agent Orchestrator** | Читает через LangChain Retriever для RAG |
| **RegionalRAGTool** | Семантический поиск по юридическим/региональным справкам |

---

## 2. Конфигурация

### Docker Compose

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: globrix-qdrant
    ports:
      - "6333:6333"  # HTTP API
      - "6334:6334"  # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

volumes:
  qdrant_data:
```

### Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `QDRANT_URL` | `http://localhost:6333` | URL Qdrant сервера |
| `QDRANT_COLLECTION_NAME` | `documents` | Название коллекции |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Модель OpenAI для эмбеддингов |
| `EMBEDDING_DIMENSIONS` | `1536` | Размерность вектора |
| `OPENAI_API_KEY` | — | API ключ для создания эмбеддингов |

---

## 3. Схема коллекции

### Конфигурация векторов

```python
VectorParams(
    size=1536,              # Размерность для text-embedding-3-small
    distance=Distance.COSINE  # Косинусное расстояние для similarity search
)
```

### Метаданные документов

Каждый chunk хранится со следующими метаданными:

| Поле | Тип | Описание |
|------|-----|----------|
| `document_id` | string | UUID документа |
| `file_name` | string | Имя исходного файла |
| `document_hash` | string | SHA256 хеш для проверки дубликатов |
| `chunk_index` | int | Индекс chunk в документе |
| `total_chunks` | int | Общее количество chunks |
| `page` | int | Номер страницы PDF (из PyMuPDF) |
| + дополнительные из события | dict | Произвольные метаданные |

---

## 4. Chunking Strategy

### Параметры разбиения

| Параметр | Значение | Описание |
|----------|----------|----------|
| `chunk_size` | 1000 | Размер chunk в символах |
| `chunk_overlap` | 200 | Перекрытие между chunks |

### Splitter

Используется `RecursiveCharacterTextSplitter`:
- Пытается разделять по параграфам и предложениям
- Сохраняет overlap для контекста между chunks
- Оптимизирован для LLM retrieval

---

## 5. API использования

### Document Consumer — запись

```python
from app.vector_store.store import get_vector_store

vector_store = get_vector_store()

# Добавление документов
ids = await vector_store.add_documents(chunks)
```

### Agent Orchestrator — чтение

```python
from services.vector_store import get_vector_store

vector_store = get_vector_store()

# Similarity search
docs = await vector_store.search(query="что такое escrow?", k=5)

# Search с scores
results = await vector_store.search_with_scores(query, k=5)

# LangChain Retriever для RAG chains
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
```

### Фильтрация по метаданным

```python
# Поиск только в документах определённого типа
docs = await vector_store.search(
    query="правила покупки",
    k=5,
    filter_metadata={"region": "Dubai"}
)
```

---

## 6. Проверка дубликатов

Система предотвращает повторную загрузку одинаковых документов:

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Проверка по SHA256 хешу
results = client.scroll(
    collection_name="documents",
    scroll_filter=Filter(
        must=[
            FieldCondition(
                key="metadata.document_hash",
                match=MatchValue(value=document_hash),
            )
        ]
    ),
    limit=1,
)

is_duplicate = len(results[0]) > 0
```

---

## 7. Мониторинг и отладка

### Web UI

Qdrant Dashboard доступен по адресу:
```
http://localhost:6333/dashboard
```

### REST API

```bash
# Информация о коллекциях
curl http://localhost:6333/collections

# Информация о конкретной коллекции
curl http://localhost:6333/collections/documents

# Количество точек
curl http://localhost:6333/collections/documents/points/count

# Поиск (пример)
curl -X POST http://localhost:6333/collections/documents/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

### Python клиент

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Список коллекций
collections = client.get_collections()

# Информация о коллекции
info = client.get_collection("documents")
print(f"Vectors count: {info.vectors_count}")
print(f"Points count: {info.points_count}")
```

---

## 8. Embedding модели

### Поддерживаемые модели OpenAI

| Модель | Размерность | Использование |
|--------|-------------|---------------|
| `text-embedding-3-small` | 1536 | По умолчанию, баланс качество/стоимость |
| `text-embedding-3-large` | 3072 | Максимальное качество |
| `text-embedding-ada-002` | 1536 | Legacy модель |

### Смена модели

При смене модели необходимо:
1. Обновить `EMBEDDING_MODEL` и `EMBEDDING_DIMENSIONS`
2. Пересоздать коллекцию (или создать новую)
3. Переиндексировать все документы

---

## 9. Данные для RAG

### Типы документов в коллекции

Документы из папки `docs/Globrix Docs/`:

| Регион | Документы |
|--------|-----------|
| **Indonesia** | Indonesia Real Estate Legal Framework and Bali Property.pdf |
| **Malaysia** | Malaysian Real Estate: Legal Guide and Regional Market.pdf |
| **Thailand** | Thailand Real Estate Legal Guide, Thailand Real Estate Terms |

### Примеры запросов

```python
# Юридические вопросы
docs = await vector_store.search("ограничения для иностранцев при покупке недвижимости")

# Терминология
docs = await vector_store.search("что такое DLD fees")

# Региональная специфика
docs = await vector_store.search("правила владения виллой в Бали")
```

---

## 10. Production рекомендации

### Масштабирование

- Для production рекомендуется Qdrant Cloud или кластер
- gRPC порт (6334) обеспечивает более быстрый доступ
- Используйте persistent volume для данных

### Безопасность

```yaml
environment:
  QDRANT__SERVICE__API_KEY: "your-secure-api-key"
```

### Backup

```bash
# Snapshot коллекции
curl -X POST "http://localhost:6333/collections/documents/snapshots"

# Список snapshots
curl "http://localhost:6333/collections/documents/snapshots"
```

---

## Полезные ссылки

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Qdrant Integration](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
