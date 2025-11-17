# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY api/ ./api/

# Install dependencies
WORKDIR /app/api
RUN pip install --upgrade pip && \
    pip install fastapi uvicorn python-multipart python-dotenv && \
    pip install openai pymupdf pillow && \
    pip install pinecone-client && \
    pip install langchain langchain-core langchain-openai langchain-text-splitters langchain-experimental

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
