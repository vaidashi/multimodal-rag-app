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


class VectorSearchInput(BaseModel):
    """Schema for vector search input."""

    query: str = Field(description="The user's question, for semantic search.")
    filename: str | None = Field(
        default=None, description="Optional filename to filter the search."
    )


class GraphExtractionInput(BaseModel):
    """Schema for graph extraction input."""

    query: str = Field(description="The user's question to extract the graph.")
    filename: str | None = Field(
        description="The name of the optional file to extract the graph from."
    )
