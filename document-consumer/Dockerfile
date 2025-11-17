FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies (keep pip cache, install in editable mode)
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# Copy application code
COPY app ./app

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000

# Run the application with Faststream CLI
CMD ["faststream", "run", "app.main:app"]
