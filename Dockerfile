# =============================================================================
# Chatbot Project - Dockerfile
# Multi-stage build for AWS Lambda deployment (or standalone API server).
# =============================================================================

# ---- Base stage with dependencies ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies (required for spaCy and torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# ---- Development stage (standalone API server) ----
FROM base AS dev

COPY . .

# Run API with uvicorn (for local development)
EXPOSE 8080
CMD ["uvicorn", "src.api.local_server:app", "--host", "0.0.0.0", "--port", "8080"]

# ---- Lambda stage (for AWS deployment) ----
FROM base AS lambda

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

COPY . .

# Copy the Lambda runtime interface entrypoint
ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["src.api.lambda_handler.lambda_handler"]