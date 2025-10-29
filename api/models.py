from pydantic import BaseModel
from typing import List


class DocumentChunk(BaseModel):
    """Schema for a single chunk of a document."""

    text: str
    metadata: dict


class IngestResponse(BaseModel):
    """Schema for the response of the ingest endpoint."""

    message: str
    file_name: str
    vector_count: int
