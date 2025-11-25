# Document Consumer - RAG система

Сервис для обработки PDF документов и семантического поиска с использованием RAG (Retrieval Augmented Generation).

## Что реализовано (Этап 1) ✅

### 1. Базовая инфраструктура
- **FastStream проект** с поддержкой RabbitMQ
- **Qdrant векторная БД** запущена в Docker
- **Класс DocumentVectorStore** для работы с векторным хранилищем (Singleton pattern)
- **Настройки** через .env файл
- **Pytest тесты** для всех компонентов

### 2. Технологический стек
- **FastStream** - асинхронная работа с RabbitMQ
- **LangChain** - фреймворк для RAG пайплайна
- **Qdrant** - векторная база данных
- **OpenAI text-embedding-3-small** - модель эмбеддингов
- **Docker Compose** - оркестрация сервисов

### 3. Структура проекта
```
document-consumer/
├── app/
│   ├── config/
│   │   └── settings.py          # Настройки приложения
│   ├── consumers/
│   │   └── document_consumer.py # Обработчики RabbitMQ (пока пустой)
│   ├── models/
│   │   └── __init__.py          # Модели данных (будет в Этапе 2)
│   ├── vector_store/
│   │   └── store.py             # Класс для работы с Qdrant
│   └── main.py                  # Точка входа FastStream
├── tests/
│   ├── test_config.py           # Тесты настроек
│   └── test_vector_store.py     # Тесты векторного хранилища
├── docker-compose.yml           # RabbitMQ + Qdrant
├── pyproject.toml               # Зависимости
├── pytest.ini                   # Конфигурация pytest
└── .env                         # Переменные окружения (не в git!)
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

### 4. Запуск тестов
```bash
# Запустить все тесты
uv run pytest -v

# Только unit тесты (быстрые)
uv run pytest tests/test_config.py -v

# Только integration тесты
uv run pytest tests/test_vector_store.py -v
```

## Доступ к сервисам

- **RabbitMQ Management UI**: http://localhost:15672 (guest/guest)
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Qdrant API**: http://localhost:6333

## Что дальше (Этап 2)

В следующем этапе будет реализовано:
- Обработчик сообщений из RabbitMQ
- Декодирование PDF из base64
- Разбиение документов на chunks с помощью LangChain
- Сохранение в Qdrant с автоматическим созданием эмбеддингов
- API для поиска в документах
