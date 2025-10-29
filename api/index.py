from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from models import IngestResponse, DocumentChunk

from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

app = FastAPI()

app = FastAPI(
    title="Multi-Modal RAG API",
    description="API for handling document ingestion and querying.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """
    A simple health check endpoint.
    """
    return {"status": "ok", "message": "Backend is running!"}


@app.get("/")
def read_root():
    return {"backend": "root endpoint"}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingests and processes a text document.

    - Accepts a .txt file.
    - Reads the content.
    - Chunks the text into smaller, manageable pieces.
    - Returns the chunks.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400, detail="Only .txt files are supported for now."
        )

    try:
        # Read the file content
        contents = await file.read()
        text = contents.decode("utf-8")

        # 1. Initialize the Text Splitter
        # chunk_size: The maximum size of each chunk (in characters).
        # chunk_overlap: The number of characters to overlap between chunks.
        # This overlap helps maintain context between chunks.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # 2. Split the text into chunks
        split_texts = text_splitter.split_text(text)

        # 3. Format the chunks using Pydantic model
        chunks = [DocumentChunk(text=t) for t in split_texts]

        return IngestResponse(
            message="File ingested and chunked successfully.",
            file_name=file.filename,
            chunks=chunks,
        )
    except Exception as e:
        # Generic error handler for any other issues
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
