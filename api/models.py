from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentChunk(BaseModel):
    """Schema for a single chunk of a document."""

    text: str
    metadata: dict


class IngestResponse(BaseModel):
    """Schema for the response of the ingest endpoint."""

    message: str
    file_name: str
    vector_count: int


class DocumentSource(BaseModel):
    """Schema for a source document chunk."""

    text: str = Field(description="The text content of the document chunk.")
    source: str = Field(description="The name of the source file.")


class ChatRequest(BaseModel):
    """Schema for a chat query."""

    query: str
    filename: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for the chat response."""

    answer: str
    sources: List[DocumentSource]
    graph_data: List[str] = []


class TTSRequest(BaseModel):
    """Schema for text-to-speech request."""

    text: str
