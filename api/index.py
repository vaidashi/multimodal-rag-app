from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import List
from models import (
    IngestResponse,
    ChatRequest,
    ChatResponse,
    DocumentSource,
    TTSRequest,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
import base64
import fitz
from fastapi.responses import StreamingResponse
from openai import OpenAI
import networkx as nx
from langchain_experimental.graph_transformers import LLMGraphTransformer

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
    Ingests and processes a document (text, PDF, or image).

    - Accepts a file upload.
    - Reads the content.
    - Chunks the content into smaller, manageable pieces.
    - Returns the chunks.
    """
    file_extension = os.path.splitext(file.filename)[1].lower()
    contents = await file.read()

    documents_to_embed = []

    vision_llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0
    )

    try:
        if file_extension == ".txt":
            documents_to_embed = process_text(contents.decode("utf-8"), file.filename)
        elif file_extension == ".pdf":
            documents_to_embed = process_pdf(contents, file.filename, vision_llm)
        elif file_extension in [".png", ".jpg", ".jpeg"]:
            documents_to_embed = process_image(contents, file.filename, vision_llm)
        else:
            raise HTTPException(
                status_code=400, detail=f"File type '{file_extension}' not supported."
            )

        if not documents_to_embed:
            raise HTTPException(
                status_code=400, detail="Could not extract any content from the file."
            )

        print(f"Successfully processed {len(documents_to_embed)} document chunks")

        texts_for_embedding = [doc["text"] for doc in documents_to_embed]
        metadata_for_pinecone = [doc["metadata"] for doc in documents_to_embed]

        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small"
        )

        print(
            f"Embedding and upserting {len(texts_for_embedding)} chunks to Pinecone..."
        )
        print(f"Index name: {INDEX_NAME}")
        print(
            f"Sample metadata: {metadata_for_pinecone[0] if metadata_for_pinecone else 'None'}"
        )

        vector_store = Pinecone.from_texts(
            texts=texts_for_embedding,
            embedding=embeddings,
            metadatas=metadata_for_pinecone,
            index_name=INDEX_NAME,
        )

        print(f"Upsert complete. Total vectors stored: {len(texts_for_embedding)}")

        # Verify data was stored by doing a quick test search
        try:
            test_results = vector_store.similarity_search("test", k=1)
            print(
                f"Verification: Index contains data (found {len(test_results)} result(s))"
            )
        except Exception as e:
            print(f"Verification warning: Could not query index: {str(e)}")

        return IngestResponse(
            message="File ingested and vectors stored successfully.",
            file_name=file.filename,
            vector_count=len(texts_for_embedding),
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    Handles chat queries against the ingested documents.
    Can be scoped to a specific document if filename is provided.

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
        print(f"Connecting to Pinecone index: {INDEX_NAME}")
        vector_store = Pinecone.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings,
        )

        print(f"Successfully connected to Pinecone index: {INDEX_NAME}")

        # Determine retrieval settings
        num_docs = 5
        search_kwargs = {"k": num_docs}

        # Add metadata filter if filename is provided
        if request.filename:
            print(f"Adding Pinecone metadata filter for: '{request.filename}'")
            # Filter by the 'filename' field which contains just the filename, not page numbers
            search_kwargs["filter"] = {"filename": {"$eq": request.filename}}

        print(f"Search configuration: {search_kwargs}")

        # Retrieve relevant documents
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs=search_kwargs
        )

        # Get documents
        print(f"Querying vector store with: '{request.query}'")
        retrieved_docs = retriever.invoke(request.query)

        print(f"Retrieved {len(retrieved_docs)} documents for query: '{request.query}'")

        # Debug: show what sources we got
        if retrieved_docs:
            print("Retrieved documents:")
            for i, doc in enumerate(retrieved_docs[:5]):
                source_val = doc.metadata.get("source", "MISSING")
                print(
                    f"  [{i}] source: '{source_val}', content preview: {doc.page_content[:80]}..."
                )
        else:
            print("WARNING: No documents retrieved!")
            if request.filename:
                print(f"  - Tried filtering for filename: '{request.filename}'")
                print("  - Check if metadata was stored correctly during ingestion")
            else:
                print("  - No filename filter was applied")
                print(
                    "  - The vector store may be empty or the query didn't match anything"
                )

        # Graph extraction
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        graph_data = extract_and_build_graph(retrieved_texts, llm)

        # Format the context from retrieved documents
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

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

        # Create a simple chain using the already-retrieved documents
        chain = prompt | llm | StrOutputParser()

        # Invoke the chain with the formatted context and query
        answer = chain.invoke({"question": request.query, "context": context})

        # Format sources for the response
        sources = [
            DocumentSource(
                text=doc.page_content, source=doc.metadata.get("source", "Unknown")
            )
            for doc in retrieved_docs
        ]

        return ChatResponse(answer=answer, sources=sources, graph_data=graph_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred in the chat endpoint: {str(e)}"
        )


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Converts text to speech using OpenAI's TTS capabilities.

    - Accepts a text string.
    - Generates speech audio.
    - Returns the audio as a streaming response.
    """
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        print("Generating speech audio...")
        tts_response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=request.text,
            response_format="mp3",
        )

        return StreamingResponse(
            tts_response.iter_bytes(),
            media_type="audio/mpeg",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred in the TTS endpoint: {str(e)}"
        )


def get_image_description(image_bytes: bytes, llm: ChatOpenAI) -> str:
    """Gets a text description of an image using a vision model.

    Args:
        image_bytes (bytes): The raw bytes of the image.
        llm (ChatOpenAI): The OpenAI vision model for image description.

    Returns:
        str: A text description of the image.
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Describe this image in detail. What objects are present? What is happening? What text is visible?",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                },
            ]
        )
    ]

    try:
        print("Getting image description from vision model...")
        response = llm.invoke(prompt)
        print("Description received.")
        return response.content
    except Exception as e:
        print(f"Error getting image description: {str(e)}")
        return "Error: Could not generate image description"


def process_text(text: str, filename: str) -> List[dict]:
    """Processes text into chunks with metadata.

    Args:
        text (str): The raw text to process.
        filename (str): The source filename for metadata.

    Returns:
        List[dict]: A list of dictionaries containing text chunks and metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    split_texts = text_splitter.split_text(text)

    documents_with_metadata = [
        {"text": doc, "metadata": {"source": filename, "filename": filename}}
        for doc in split_texts
    ]

    return documents_with_metadata


def process_pdf(file_bytes: bytes, filename: str, llm: ChatOpenAI) -> List[dict]:
    """Processes a PDF file into text chunks with metadata.

    Args:
        file_bytes (bytes): The raw bytes of the PDF file.
        filename (str): The source filename for metadata.
        llm (ChatOpenAI): The OpenAI vision model for image description.

    Returns:
        List[dict]: A list of dictionaries containing text chunks and metadata.
    """
    documents_with_metadata = []

    pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")

    print(f"Processing PDF '{filename}' with {pdf_doc.page_count} pages...")

    for page_num, page in enumerate(pdf_doc):
        print(f"Processing page {page_num + 1}/{pdf_doc.page_count}...")
        text = page.get_text()

        # Strip whitespace and check if there's meaningful text
        if text and text.strip():
            page_text_chunks = process_text(text, f"{filename}_page_{page_num + 1}")
            # Add filename to each chunk's metadata for filtering
            for chunk in page_text_chunks:
                chunk["metadata"]["filename"] = filename
            documents_with_metadata.extend(page_text_chunks)
            print(f"  - Extracted {len(page_text_chunks)} text chunk(s)")

        # Process images on the page (limit to avoid timeouts)
        images = page.get_images(full=True)

        if images:
            print(f"  - Found {len(images)} image(s) on page {page_num + 1}")

        for img_index, img in enumerate(images[:5]):  # Limit to first 5 images per page
            try:
                xref = img[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Skip very small images (likely decorative)
                if len(image_bytes) < 1024:  # Less than 1KB
                    continue

                print(f"  - Processing image {img_index + 1}...")
                description = get_image_description(image_bytes, llm)
                image_chunk = {
                    "text": f"Image description: {description}",
                    "metadata": {
                        "source": f"{filename}_page_{page_num + 1}_image_{img_index + 1}",
                        "filename": filename,
                    },
                }
                documents_with_metadata.append(image_chunk)
            except Exception as e:
                print(f"  - Error processing image {img_index + 1}: {str(e)}")
                continue

    pdf_doc.close()
    print(f"PDF processing complete. Total chunks: {len(documents_with_metadata)}")
    return documents_with_metadata


def process_image(file_bytes: bytes, filename: str, llm: ChatOpenAI) -> List[dict]:
    """Processes an image file into a text chunk with metadata.

    Args:
        file_bytes (bytes): The raw bytes of the image file.
        filename (str): The source filename for metadata.
        llm (ChatOpenAI): The OpenAI vision model for image description.

    Returns:
        List[dict]: A list containing a single dictionary with the image description and metadata.
    """
    description = get_image_description(file_bytes, llm)
    document_with_metadata = {
        "text": f"Image description: {description}",
        "metadata": {"source": filename, "filename": filename},
    }
    return [document_with_metadata]


def extract_and_build_graph(text_chunks: List[str], llm: ChatOpenAI) -> List[str]:
    """Extracts knowledge triples from text chunks and returms them as formatted strings.

    Args:
        text_chunks (List[str]): A list of text chunks
        llm (ChatOpenAI): The OpenAI model

    Returns:
        List[str]: List of formatted knowledge triples as strings.
    """

    if not text_chunks:
        return []

    graph_extraction_llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0
    )

    llm_transformer = LLMGraphTransformer(
        llm=graph_extraction_llm,
    )

    full_text = "\n\n".join(text_chunks)

    try:
        print("Extracting knowledge triples from text chunks...")
        # Create a proper Document object for LangChain
        documents = [Document(page_content=full_text)]
        graph_documents = llm_transformer.convert_to_graph_documents(documents)

        if not graph_documents:
            print("No graph documents were created.")
            return []

        # Extract nodes and relationships from the GraphDocument
        graph_doc = graph_documents[0]
        formatted_triples = []

        # Process relationships (edges in the knowledge graph)
        for relationship in graph_doc.relationships:
            subject = relationship.source.id
            object_ = relationship.target.id
            rel_type = relationship.type
            formatted_triples.append(f"{subject} --{rel_type}--> {object_}")

        print(f"Extracted {len(formatted_triples)} knowledge triples.")
        return formatted_triples
    except Exception as e:
        print(f"Error extracting knowledge triples: {str(e)}")
        return []
