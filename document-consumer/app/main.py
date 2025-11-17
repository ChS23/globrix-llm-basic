"""Main Faststream application entrypoint."""

import structlog
from faststream import FastStream
from faststream.kafka import KafkaBroker

from app.config.settings import settings
from app.consumers.document_consumer import router as document_router
from app.utils.logging import configure_logging

# Configure logging
configure_logging(debug=settings.debug)
logger = structlog.get_logger()

# Initialize Kafka broker
broker = KafkaBroker(
    bootstrap_servers=settings.kafka_bootstrap_servers,
)

# Create FastStream app
app = FastStream(broker)

# Include routers
broker.include_router(document_router)


@app.on_startup
async def on_startup() -> None:
    """Execute on application startup."""
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        version=settings.app_version,
        kafka_servers=settings.kafka_bootstrap_servers,
        vector_store=settings.vector_store_type,
    )


@app.on_shutdown
async def on_shutdown() -> None:
    """Execute on application shutdown."""
    logger.info("shutting_down_application")


@app.after_startup
async def after_startup() -> None:
    """Execute after application startup."""
    logger.info(
        "application_ready",
        topics={
            "ingest": settings.kafka_topic_documents_ingest,
            "processed": settings.kafka_topic_documents_processed,
            "query_requests": settings.kafka_topic_query_requests,
            "query_responses": settings.kafka_topic_query_responses,
        },
    )


# No need for __main__ block when using faststream CLI
