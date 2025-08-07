# syntax=docker/dockerfile:1

# Stage 1: Build image (for dependencies)
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build deps and pip tools
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY src ./src
COPY requirements.txt .
ENV PATH=/root/.local/bin:$PATH

# Optional: create non-root user (recommended for prod)
RUN useradd -m processor
USER processor

# Expose port 8000 for FastAPI
EXPOSE 8000

# Entrypoint: Uvicorn in production mode
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
