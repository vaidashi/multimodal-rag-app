import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "multimodal-rag-index"
EMBEDDING_DIMENSION = 1536  # Dimension for OpenAI's text-embedding-3-small


def create_pinecone_index():
    """
    Connects to Pinecone and creates a serverless index if not already exists.
    """

    if not PINECONE_API_KEY:
        print("PINECONE_API_KEY is not set. Please set it in the .env file.")
        return

    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if INDEX_NAME in pc.list_indexes().names():
        print(f"Index {INDEX_NAME} already exists. Skipping creation.")
        print(
            "You can view your index here:",
            f"https://app.pinecone.io/indexes/{INDEX_NAME}",
        )
        return

    print(f"Creating index {INDEX_NAME}...")
    try:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
        )

        # Wait until the index is ready
        while not pc.describe_index(INDEX_NAME).status().ready:
            print("Waiting for index to be ready...")
            time.sleep(5)
        print(f"Index {INDEX_NAME} created successfully!")
        print(
            "You can view your index here:",
            f"https://app.pinecone.io/indexes/{INDEX_NAME}",
        )
    except Exception as e:
        print(f"An error occurred while creating the index: {str(e)}")


if __name__ == "__main__":
    create_pinecone_index()
