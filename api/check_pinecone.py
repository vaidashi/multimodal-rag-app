"""Quick script to check what documents are in Pinecone."""

import os
from dotenv import load_dotenv
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "multimodal-rag-index"

embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small"
)

vector_store = Pinecone.from_existing_index(
    index_name=INDEX_NAME,
    embedding=embeddings,
)

# Search without any filter to see what's there
print("Searching Pinecone without filters...")
results = vector_store.similarity_search("Project Alpha", k=10)

print(f"\nFound {len(results)} documents")
print("\nDocument metadata:")
for i, doc in enumerate(results):
    print(f"\n[{i}] Filename: '{doc.metadata.get('filename', 'MISSING')}'")
    print(f"    Source: '{doc.metadata.get('source', 'MISSING')}'")
    print(f"    Content preview: {doc.page_content[:100]}...")

# Now try with the filter
print("\n" + "=" * 50)
print("Searching with filter: filename='evaluation_doc.txt'")
results_filtered = vector_store.similarity_search(
    "Project Alpha", k=10, filter={"filename": {"$eq": "evaluation_doc.txt"}}
)
print(f"Found {len(results_filtered)} documents with filter")
