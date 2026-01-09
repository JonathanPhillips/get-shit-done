# Multi-stage build for Focus Agent Backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

# Development command (can be overridden)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY src ./src

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Production command (single worker for SQLite compatibility)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
