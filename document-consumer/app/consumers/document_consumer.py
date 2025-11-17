"""Document consumer for processing document ingestion events."""

import time
from typing import Any

import structlog
from faststream.kafka import KafkaRouter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.config.settings import settings
from app.models.events import (
    DocumentIngestEvent,
    DocumentProcessedEvent,
    DocumentStatus,
)
from app.vector_store.manager import VectorStoreManager

logger = structlog.get_logger()

# Create router for document-related topics
router = KafkaRouter()

# Get vector store instance
vector_store = VectorStoreManager.get_vector_store()


@router.subscriber(settings.kafka_topic_documents_ingest)
@router.publisher(settings.kafka_topic_documents_processed)
async def process_document_ingest(
    event: DocumentIngestEvent,
) -> DocumentProcessedEvent:
    """Process document ingestion event.

    This handler:
    1. Receives document metadata from Kafka
    2. Downloads document from MinIO
    3. Processes document (load, chunk, embed)
    4. Stores in vector database
    5. Publishes processing result

    Args:
        event: Document ingestion event

    Returns:
        DocumentProcessedEvent with processing result
    """
    start_time = time.time()

    logger.info(
        "processing_document",
        document_id=event.document_id,
        file_name=event.file_name,
        country=event.country,
        category=event.category,
    )

    try:
        # 1. Load document with LangChain loader
        # TODO: Add MinIO download support (for now use local file path)
        logger.info("loading_document", file_path=event.file_path)

        if event.file_type == "pdf":
            loader = PyPDFLoader(event.file_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file type: {event.file_type}")

        logger.info("document_loaded", pages_count=len(documents))

        # 2. Chunk document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)

        logger.info("document_chunked", chunks_count=len(chunks))

        # 3. Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "document_id": event.document_id,
                "file_name": event.file_name,
                "country": event.country,
                "category": event.category,
                "language": event.language,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })

        # 4. Store in vector DB (embeddings generated automatically)
        logger.info("storing_chunks_in_vector_db", chunks_count=len(chunks))
        doc_ids = await vector_store.add_documents(chunks)

        logger.info(
            "chunks_stored",
            chunks_count=len(doc_ids),
            sample_ids=doc_ids[:3],
        )

        processing_time = time.time() - start_time

        logger.info(
            "document_processed_successfully",
            document_id=event.document_id,
            chunks_count=len(chunks),
            processing_time=processing_time,
        )

        return DocumentProcessedEvent(
            document_id=event.document_id,
            status=DocumentStatus.COMPLETED,
            chunks_count=len(chunks),
            processing_time_seconds=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time

        logger.error(
            "document_processing_failed",
            document_id=event.document_id,
            error=str(e),
            processing_time=processing_time,
            exc_info=True,
        )

        return DocumentProcessedEvent(
            document_id=event.document_id,
            status=DocumentStatus.FAILED,
            error_message=str(e),
            processing_time_seconds=processing_time,
        )
