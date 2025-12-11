"""
Настройки приложения.

Все настройки загружаются из переменных окружения (.env файл).
Это безопасно, потому что API ключи не хранятся в коде.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс с настройками приложения.

    Pydantic автоматически:
    - Загружает значения из .env файла
    - Проверяет типы данных
    - Подставляет значения по умолчанию
    """

    # Основные настройки
    app_name: str = "document-consumer"
    app_version: str = "0.1.0"

    # RabbitMQ - брокер сообщений
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="URL для подключения к RabbitMQ"
    )

    # Топики (очереди) RabbitMQ
    topic_documents_ingest: str = Field(
        default="documents.ingest",
        description="Топик для получения новых документов"
    )

    # Qdrant - векторная база данных
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="URL для подключения к Qdrant"
    )
    qdrant_collection_name: str = Field(
        default="documents",
        description="Название коллекции в Qdrant"
    )

    # Эмбеддинги - настройки модели
    openai_api_key: str = Field(
        default="",
        description="OpenAI API ключ (используется для эмбеддингов и evaluation)"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Название модели эмбеддингов (например: text-embedding-3-small, text-embedding-3-large)"
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Размер вектора эмбеддинга (зависит от модели: 1536 для text-embedding-3-small, 3072 для large)"
    )

    # Параметры chunking (разбиение документа на кусочки)
    chunk_size: int = Field(
        default=1000,
        description="Размер одного кусочка текста в символах"
    )
    chunk_overlap: int = Field(
        default=200,
        description="Перекрытие между кусочками в символах (чтобы не терять контекст)"
    )

    # Evaluation - настройки для метрик
    evaluation_model: str = Field(
        default="gpt-4o-mini",
        description="Модель для LLM-as-a-judge метрик (gpt-4o-mini, gpt-4o, claude-3-5-sonnet, etc.)"
    )

    # Evaluation - пороги для метрик (0.0 - 1.0)
    eval_threshold_context_precision: float = Field(
        default=0.8,
        description="Минимальный порог для Context Precision (ранжирование документов)"
    )
    eval_threshold_context_relevancy: float = Field(
        default=0.9,
        description="Минимальный порог для Context Relevancy (релевантность контекста)"
    )
    eval_threshold_context_recall: float = Field(
        default=0.9,
        description="Минимальный порог для Context Recall (полнота извлечения)"
    )
    eval_threshold_faithfulness: float = Field(
        default=0.9,
        description="Минимальный порог для Faithfulness (отсутствие галлюцинаций)"
    )
    eval_threshold_answer_relevancy: float = Field(
        default=0.85,
        description="Минимальный порог для Answer Relevancy (релевантность ответа)"
    )
    eval_threshold_semantic_similarity: float = Field(
        default=0.85,
        description="Минимальный порог для Semantic Similarity (семантическая близость к эталону)"
    )

    # Конфигурация Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Глобальный экземпляр настроек
# Используется во всем приложении
settings = Settings()
