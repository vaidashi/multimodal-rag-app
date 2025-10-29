from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import List
from models import (
    IngestResponse,
    DocumentChunk,
    ChatRequest,
    ChatResponse,
    DocumentSource,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise RuntimeError(
        "API keys for OpenAI and/or Pinecone are not set in the environment."
    )

INDEX_NAME = "multimodal-rag-index"


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

        # Initialize the Text Splitter
        # chunk_size: The maximum size of each chunk (in characters).
        # chunk_overlap: The number of characters to overlap between chunks.
        # This overlap helps maintain context between chunks.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Split the text into chunks
        split_texts = text_splitter.split_text(text)

        # Add metadata to each chunk
        documents_with_metadata = [
            {"text": doc, "metadata": {"source": file.filename}} for doc in split_texts
        ]

        texts_for_embedding = [doc["text"] for doc in documents_with_metadata]
        metadata_for_pinecone = [doc["metadata"] for doc in documents_with_metadata]

        # Initialize embeddings model
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small"
        )

        print(
            f"Embedding and upserting {len(texts_for_embedding)} chunks to Pinecone..."
        )

        Pinecone.from_texts(
            texts=texts_for_embedding,
            embedding=embeddings,
            metadatas=metadata_for_pinecone,
            index_name=INDEX_NAME,
        )

        print("Upsert complete.")

        return IngestResponse(
            message="File ingested and vectors stored successfully.",
            file_name=file.filename,
            vector_count=len(split_texts),
        )
    except Exception as e:
        # Generic error handler for any other issues
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    Handles chat queries against the ingested documents.

    - Accepts a query string.
    - Retrieves relevant document chunks from Pinecone.
    - Generates an answer using OpenAI's language model.
    - Returns the answer along with source document information.
    """
    try:
        # Initialize embeddings model
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small"
        )
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0
        )

        # Initialize Pinecone vector store
        vector_store = Pinecone.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings,
        )

        # Retrieve relevant documents
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

        # Get documents
        retrieved_docs = retriever.invoke(request.query)

        template = """
        You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        Keep the answer concise.

        Question: {question}
        Context: {context}
        Answer:
        """
        prompt = PromptTemplate.from_template(template)

        # Construct the RAG Chain using LCEL
        def format_docs(docs: List[Document]) -> str:
            """Helper function to format retrieved documents into a single string."""
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Invoke the chain with the user's query
        answer = rag_chain.invoke(request.query)

        # Format sources for the response
        sources = [
            DocumentSource(
                text=doc.page_content, source=doc.metadata.get("source", "Unknown")
            )
            for doc in retrieved_docs
        ]

        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred in the chat endpoint: {str(e)}"
        )
