# Backend Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY api/ .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv && \
    pip install --no-cache-dir openai pymupdf pillow && \
    pip install --no-cache-dir pinecone && \
    pip install --no-cache-dir langchain langchain-core langchain-openai && \
    pip install --no-cache-dir langchain-text-splitters langchain-experimental && \
    pip install --no-cache-dir networkx pandas ragas datasets httpx

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
