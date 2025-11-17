# Document Consumer - RAG Service

RAG-based document processing service built with **LangChain** and **Faststream** for Globrix real estate platform.

## 🎯 Overview

This service processes real estate documents from multiple countries with different legal systems and terminology.

### Current Status: **Foundation Complete** ✅

**Implemented:**
- ✅ Faststream application with Kafka integration
- ✅ Event-driven architecture (document ingestion & query patterns)
- ✅ Pydantic models for type-safe events
- ✅ Structured logging with structlog
- ✅ Configuration management with environment variables
- ✅ Docker infrastructure (Kafka, Qdrant, MinIO)
- ✅ Vector store abstraction layer

**In Progress:**
- 🔄 Document processing pipeline (loading, chunking, embeddings)
- 🔄 Vector store integration (Qdrant client implementation)
- 🔄 Query consumer and RAG pipeline

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Kafka Topics                              │
│  documents.ingest → documents.processed                      │
│  query.requests → query.responses                            │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────────┐
│              Document Consumer (Faststream)                  │
│  ┌────────────────────────────────────────────────────┐      │
│  │ Event Handlers (async)                             │      │
│  │  • process_document_ingest()                       │      │
│  │  • handle_query_request() [TODO]                   │      │
│  └────────────────────────────────────────────────────┘      │
└────────────────────┬─────────────────────────────────────────┘
                     │
      ┌──────────────┴───────────────┐
      ↓                              ↓
┌─────────────┐              ┌──────────────┐
│   MinIO     │              │   Qdrant     │
│  (Storage)  │              │  (Vectors)   │
└─────────────┘              └──────────────┘
```

## 📦 Tech Stack

- **Faststream 0.5+**: Async Kafka event processing framework
- **LangChain**: Document loading and RAG pipelines (to be integrated)
- **Qdrant**: Vector database with hybrid search support
- **MinIO**: S3-compatible object storage for documents
- **Kafka + Zookeeper**: Event streaming platform
- **Pydantic 2.0**: Type-safe data validation and settings

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### 1. Setup Environment

```bash
cd document-consumer

# Copy environment template
cp .env.example .env

# (Optional) Edit .env with your API keys
# nano .env
```

### 2. Start Infrastructure Services

```bash
# Start all dependencies
docker-compose up -d zookeeper kafka minio qdrant
```

**Services started:**
- ✅ Kafka: `localhost:9092` (message broker)
- ✅ MinIO: `localhost:9000` (storage), `localhost:9001` (web console)
- ✅ Qdrant: `localhost:6333` (vector DB), `localhost:6334` (gRPC)
- ✅ Zookeeper: `localhost:2181` (Kafka coordination)

Wait ~30 seconds for services to be healthy, then verify:
```bash
docker-compose ps
```

### 3. Run the Consumer

**Option A: Docker (Recommended)**
```bash
docker-compose up document-consumer
```

**Option B: Local Development**
```bash
# Install dependencies
pip install -e .

# Run application
python -m app.main
```

**Expected Output:**
```
INFO     starting_application app_name=document-consumer version=0.1.0
INFO     application_ready topics={'ingest': 'documents.ingest', ...}
```

## 📊 Kafka Topics

Current event flows:

| Topic | Direction | Purpose | Status |
|-------|-----------|---------|--------|
| `documents.ingest` | Input | Document ingestion requests | ✅ Consumer ready |
| `documents.processed` | Output | Processing results & status | ✅ Publisher ready |
| `query.requests` | Input | Query/search requests | 🔄 TODO |
| `query.responses` | Output | Query answers with sources | 🔄 TODO |

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Vector Store
VECTOR_STORE_TYPE=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embeddings
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DEVICE=cpu  # or cuda

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
RETRIEVAL_K=5
RETRIEVAL_ALPHA=0.7  # hybrid search weight
```

## 📝 Event Schemas

### DocumentIngestEvent
Send to `documents.ingest` topic to trigger document processing:

```json
{
  "document_id": "doc_001",
  "file_path": "s3://bucket/file.pdf",
  "file_name": "Thailand_Legal_Guide.pdf",
  "file_type": "pdf",
  "country": "thailand",
  "category": "legal_terms",
  "language": "en",
  "metadata": {},
  "timestamp": "2025-01-15T10:00:00Z"
}
```

**Categories:** `legal_terms`, `ownership_rules`, `taxes_fees`, `property_listing`, `market_analysis`

### DocumentProcessedEvent
Published to `documents.processed` after processing:

```json
{
  "document_id": "doc_001",
  "status": "completed",
  "chunks_count": 0,
  "error_message": null,
  "processing_time_seconds": 1.23,
  "timestamp": "2025-01-15T10:00:01Z"
}
```

**Statuses:** `pending`, `processing`, `completed`, `failed`

## 🧪 Testing the Current Setup

### Verify Infrastructure

```bash
# Check all services are healthy
docker-compose ps

# Test Kafka
docker exec -it globrix-kafka kafka-topics --list --bootstrap-server localhost:9092

# Test MinIO
curl http://localhost:9000/minio/health/live

# Test Qdrant
curl http://localhost:6333/collections
```

### Send Test Event

The consumer currently accepts events and logs them (actual processing TODO):

```bash
# Using kcat (kafkacat)
echo '{
  "document_id": "test_001",
  "file_path": "s3://documents/test.pdf",
  "file_name": "test.pdf",
  "file_type": "pdf",
  "country": "thailand",
  "category": "legal_terms",
  "language": "en",
  "metadata": {}
}' | kcat -P -b localhost:9092 -t documents.ingest

# Check consumer logs
docker-compose logs -f document-consumer
```

**Expected Log Output:**
```
INFO  processing_document document_id=test_001 file_name=test.pdf country=thailand
INFO  document_processed_successfully document_id=test_001 chunks_count=0
```

## 🧪 Unit Testing

> **Note:** Test suite to be implemented

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/

# Run all checks
black app/ && ruff check app/ && mypy app/
```

### Local Development Tips

1. **Watch logs in real-time:**
   ```bash
   docker-compose logs -f document-consumer
   ```

2. **Restart consumer after code changes:**
   ```bash
   docker-compose restart document-consumer
   ```

3. **Access MinIO console:**
   - URL: http://localhost:9001
   - User/Pass: `minioadmin`/`minioadmin`

4. **Check Qdrant collections:**
   ```bash
   curl http://localhost:6333/collections
   ```

### Troubleshooting

**Kafka connection issues:**
```bash
# Check Kafka is ready
docker-compose logs kafka | grep "started"

# Manually create topics (auto-create is enabled, but if needed)
docker exec -it globrix-kafka kafka-topics --create \
  --topic documents.ingest \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

**Consumer not processing:**
```bash
# Check consumer group
docker exec -it globrix-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group document-consumer-group --describe

# Reset offset (if needed)
docker-compose down document-consumer
docker-compose up document-consumer
```

**Dependency issues:**
```bash
# Rebuild with no cache
docker-compose build --no-cache document-consumer

# Check Python dependencies
docker-compose run document-consumer pip list
```

## 📚 Project Structure

```
document-consumer/
├── app/
│   ├── main.py                       # ✅ Faststream app entrypoint
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               # ✅ Pydantic settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── events.py                 # ✅ Event schemas (Ingest, Processed, Query)
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── document_consumer.py      # ✅ Document ingestion handler (stub)
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── base.py                   # ✅ Abstract base class
│   │   ├── manager.py                # ✅ Factory pattern
│   │   └── qdrant_store.py          # 🔄 Qdrant implementation (partial)
│   └── utils/
│       ├── __init__.py
│       └── logging.py                # ✅ Structured logging config
├── test_data/                        # Sample documents for testing
├── docker-compose.yml                # ✅ Full infrastructure setup
├── Dockerfile                        # ✅ Python 3.12 image
├── pyproject.toml                    # ✅ Dependencies & tooling
├── .env.example                      # ✅ Environment template
├── .gitignore                        # ✅ Git exclusions
├── README.md                         # ✅ This file
└── RAG_IMPLEMENTATION_PLAN.md        # 📋 Detailed implementation plan
```

## 🎯 Roadmap

### Phase 1: Core RAG Pipeline (Current)
- [ ] Complete Qdrant vector store implementation
- [ ] Integrate LangChain document loaders (PDF, DOCX, HTML)
- [ ] Implement chunking strategy with RecursiveCharacterTextSplitter
- [ ] Setup multilingual embeddings (intfloat/multilingual-e5-large)
- [ ] Implement MinIO client for document download
- [ ] Add query consumer and retrieval pipeline
- [ ] Basic RAG with LLM integration (OpenAI/Mistral)

### Phase 2: Enhanced Search
- [ ] Hybrid search (dense + sparse vectors)
- [ ] Query reranking
- [ ] Metadata filtering (country, category)
- [ ] Citation extraction and source tracking

### Phase 3: Schema-Guided RAG
- [ ] Structured output extraction
- [ ] Country-specific schemas
- [ ] Validation and confidence scoring

### Phase 4: Production Readiness
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Monitoring and metrics (Prometheus)
- [ ] RAG evaluation with RAGAS
- [ ] CI/CD pipeline

## 📖 Documentation

- **[RAG_IMPLEMENTATION_PLAN.md](./RAG_IMPLEMENTATION_PLAN.md)** - Detailed architecture, experiments, and implementation strategy
- **[.env.example](./.env.example)** - Configuration reference

## 🤝 Contributing

1. Create feature branch from `rag`
2. Make changes following code style (black, ruff, mypy)
3. Update tests and documentation
4. Submit pull request to `rag` branch

## 📄 License

Proprietary - Globrix Platform
