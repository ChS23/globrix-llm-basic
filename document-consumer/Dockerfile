# Document Consumer Dockerfile
# Multi-stage build for optimal image size

FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev and evaluation dependencies)
ENV UV_HTTP_TIMEOUT=300
RUN uv sync --frozen --no-install-project --no-dev

# Production stage
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code (excluding test data and evaluation)
COPY app/ ./app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the FastStream application
CMD ["faststream", "run", "app.main:app"]
