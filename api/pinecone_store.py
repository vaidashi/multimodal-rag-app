"""Custom Pinecone vector store wrapper for LangChain without problematic dependencies."""
from typing import List, Optional, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
import os


class PineconeVectorStore:
    """Simple Pinecone vector store wrapper."""
    
    def __init__(self, index_name: str, embedding: Embeddings, pinecone_api_key: str):
        self.index_name = index_name
        self.embedding = embedding
        pc = Pinecone(api_key=pinecone_api_key)
        self.index = pc.Index(index_name)
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        index_name: str = None,
        **kwargs
    ):
        """Create vector store from texts."""
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        instance = cls(index_name, embedding, pinecone_api_key)
        
        # Generate embeddings
        embeddings = embedding.embed_documents(texts)
        
        # Prepare vectors for upsert
        vectors = []
        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            metadata["text"] = text
            vectors.append({
                "id": f"{index_name}_{i}_{hash(text)}",
                "values": emb,
                "metadata": metadata
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            instance.index.upsert(vectors=batch)
        
        return instance
    
    @classmethod
    def from_existing_index(
        cls,
        index_name: str,
        embedding: Embeddings,
        **kwargs
    ):
        """Load existing index."""
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        return cls(index_name, embedding, pinecone_api_key)
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        """Search for similar documents."""
        # Embed query
        query_embedding = self.embedding.embed_query(query)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            filter=filter,
            include_metadata=True
        )
        
        # Convert to Document objects
        documents = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            text = metadata.pop("text", "")
            documents.append(Document(page_content=text, metadata=metadata))
        
        return documents
    
    def as_retriever(self, search_type: str = "similarity", search_kwargs: Optional[dict] = None):
        """Return a retriever interface."""
        search_kwargs = search_kwargs or {}
        return PineconeRetriever(self, search_kwargs)


class PineconeRetriever:
    """Retriever interface for Pinecone."""
    
    def __init__(self, vectorstore: PineconeVectorStore, search_kwargs: dict):
        self.vectorstore = vectorstore
        self.search_kwargs = search_kwargs
    
    def invoke(self, query: str) -> List[Document]:
        """Retrieve documents."""
        return self.vectorstore.similarity_search(query, **self.search_kwargs)
