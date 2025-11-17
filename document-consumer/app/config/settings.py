"""Application settings and configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "document-consumer"
    app_version: str = "0.1.0"
    debug: bool = False

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_consumer_group: str = Field(default="document-consumer-group")

    # Topics
    kafka_topic_documents_ingest: str = Field(default="documents.ingest")
    kafka_topic_documents_processed: str = Field(default="documents.processed")
    kafka_topic_query_requests: str = Field(default="query.requests")
    kafka_topic_query_responses: str = Field(default="query.responses")

    # Vector Store
    vector_store_type: str = Field(default="qdrant")  # qdrant, milvus, weaviate
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_name: str = Field(default="globrix_docs")

    # Embeddings
    embedding_model: str = Field(default="intfloat/multilingual-e5-large")
    embedding_device: str = Field(default="cpu")  # cpu or cuda
    embedding_batch_size: int = Field(default=32)

    # MinIO / S3
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket_documents: str = Field(default="documents")
    minio_secure: bool = Field(default=False)

    # LLM
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    mistral_api_key: str = Field(default="")
    llm_model: str = Field(default="mistral-small-latest")
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=1000)

    # Chunking
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)

    # Retrieval
    retrieval_k: int = Field(default=5)
    retrieval_alpha: float = Field(default=0.7)  # weight for dense vs sparse


# Global settings instance
settings = Settings()
