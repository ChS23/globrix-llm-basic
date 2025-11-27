# Document Consumer - RAG система

Сервис для обработки PDF документов и семантического поиска с использованием RAG (Retrieval Augmented Generation).

## Что реализовано ✅

### Этап 1: Базовая инфраструктура ✅
- **FastStream проект** с поддержкой RabbitMQ и CLI
- **Qdrant векторная БД** запущена в Docker
- **Класс DocumentVectorStore** для работы с векторным хранилищем (Singleton pattern)
- **Настройки** через .env файл с Pydantic валидацией
- **Pytest тесты** для всех компонентов

### Этап 2: Обработка документов ✅
- **Модели данных** (DocumentIngestEvent, DocumentProcessedEvent)
- **DocumentIngestionService** - класс для обработки документов
- **RabbitMQ Consumer** - получение документов из очереди
- **Проверка дубликатов** через SHA256 хеширование
- **Извлечение текста** из PDF с помощью PyPDFLoader
- **Разбиение на chunks** (RecursiveCharacterTextSplitter)
- **Автоматическая векторизация** через OpenAI text-embedding-3-small
- **Сохранение в Qdrant** с метаданными
- **Unit тесты** с моками для OpenAI API

### Технологический стек
- **FastStream** - асинхронная работа с RabbitMQ
- **LangChain** - фреймворк для RAG пайплайна (загрузка PDF, chunking, векторизация)
- **Qdrant** - векторная база данных
- **OpenAI text-embedding-3-small** - модель эмбеддингов (1536 dimensions)
- **Docker Compose** - оркестрация RabbitMQ и Qdrant
- **Pytest** - тестирование с моками

### Структура проекта
```
document-consumer/
├── app/
│   ├── config/
│   │   └── settings.py              # Настройки приложения (Pydantic)
│   ├── consumers/
│   │   └── document_consumer.py     # RabbitMQ subscriber (тонкий слой)
│   ├── models/
│   │   └── events.py                # Pydantic модели для RabbitMQ
│   ├── services/
│   │   └── document_ingestion.py    # Бизнес-логика обработки документов
│   ├── vector_store/
│   │   └── store.py                 # Работа с Qdrant (Singleton)
│   └── main.py                      # Точка входа FastStream
├── tests/
│   ├── test_config.py               # Тесты настроек
│   ├── test_vector_store.py         # Интеграционные тесты Qdrant
│   ├── test_models.py               # Тесты Pydantic моделей
│   ├── test_document_ingestion.py   # Unit тесты с моками
│   └── send_test_document.py        # Скрипт для ручного тестирования
├── test_data/                       # Тестовые PDF файлы
├── docker-compose.yml               # RabbitMQ + Qdrant
├── pyproject.toml                   # Зависимости
├── pytest.ini                       # Конфигурация pytest
└── .env                             # Переменные окружения (не в git!)
```

## Быстрый старт

### 1. Установка зависимостей
```bash
# Активировать conda окружение
conda activate llm-p

# Установить зависимости через uv
uv sync --extra dev
```

### 2. Настройка .env
Создайте файл `.env` и добавьте ваш API ключ для модели эмбеддингов:
```env
EMBEDDING_API_KEY=sk-proj-ваш-ключ-здесь
```

### 3. Запуск Docker сервисов
```bash
# Запустить RabbitMQ и Qdrant
docker-compose up -d

# Проверить что сервисы запущены
docker-compose ps
```

### 4. Запуск FastStream приложения
```bash
# Запустить FastStream consumer
uv run faststream run app.main:app

# В логах вы увидите:
# - Подключение к RabbitMQ
# - Создание коллекции в Qdrant
# - Ожидание сообщений из топика documents.ingest
```

### 5. Отправка тестового документа
```bash
# В другом терминале отправьте тестовый PDF
# Убедитесь что файл test_data/Thailand_Real_Estate_Legal_Guide_Comprehensive.pdf существует
uv run python tests/send_test_document.py

# Вы увидите в логах FastStream:
# - Получение документа
# - Декодирование PDF
# - Вычисление хеша
# - Проверку дубликатов
# - Извлечение текста
# - Разбиение на chunks
# - Сохранение в Qdrant
```

### 6. Запуск тестов
```bash
# Запустить все тесты
uv run pytest -v

# Только unit тесты (без внешних зависимостей)
uv run pytest tests/test_models.py tests/test_document_ingestion.py -v

# Только integration тесты (требуют Qdrant)
uv run pytest tests/test_vector_store.py -v
```

## Доступ к сервисам

- **RabbitMQ Management UI**: http://localhost:15672 (guest/guest)
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Qdrant API**: http://localhost:6333

## Как это работает

### Пайплайн обработки документа:

1. **Получение** - Внешний сервис отправляет PDF (base64) в RabbitMQ топик `documents.ingest`
2. **Consumer** - FastStream получает сообщение и передаёт в DocumentIngestionService
3. **Декодирование** - base64 → PDF байты
4. **Хеширование** - SHA256 для проверки дубликатов
5. **Проверка дубликатов** - Поиск в Qdrant по `document_hash`
6. **Извлечение текста** - PyPDFLoader читает PDF → текст по страницам
7. **Chunking** - RecursiveCharacterTextSplitter разбивает на куски (1000 символов, overlap 200)
8. **Метаданные** - Добавление document_id, file_name, document_hash, chunk_index, country, category
9. **Векторизация** - OpenAI API превращает каждый chunk в вектор (1536 чисел)
10. **Сохранение** - Qdrant сохраняет векторы + текст + метаданные

### Проверка дубликатов:

- Вычисляется SHA256 хеш от **содержимого** PDF
- Ищется в Qdrant по метаданным: `metadata.document_hash == hash`
- Если найден → статус "duplicate", обработка прерывается
- Если не найден → документ обрабатывается и сохраняется

## Следующие шаги (Этап 3)

- [ ] API для поиска документов (REST endpoint или LangChain Tool для Agent Orchestrator)
- [ ] Интеграция с Agent Orchestrator
- [ ] Дополнительные форматы документов (DOCX, TXT)
- [ ] Улучшение chunking стратегии
- [ ] Мониторинг и метрики
