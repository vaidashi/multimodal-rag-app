from pydantic import BaseModel
from typing import List


class DocumentChunk(BaseModel):
    """Schema for a single chunk of a document."""

    text: str
    # add metadata later, like source file name
    # metadata: dict


class IngestResponse(BaseModel):
    """Schema for the response of the ingest endpoint."""

    message: str
    file_name: str
    chunks: List[DocumentChunk]
