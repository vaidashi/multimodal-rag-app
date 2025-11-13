import pytest
import httpx
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to Python path to import from index.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from index import app, process_text

pytestmark = pytest.mark.asyncio


# --- Test 1: Simple Helper Function ---
def test_process_text():
    """Tests the process_text helper function for correct chunking and metadata."""
    sample_text = "This is the first sentence. This is the second sentence."
    filename = "sample.txt"

    result = process_text(sample_text, filename)

    assert isinstance(result, list)
    assert len(result) == 1
    chunk = result[0]
    assert "text" in chunk
    assert "metadata" in chunk
    assert chunk["metadata"]["source"] == filename
    assert chunk["metadata"]["filename"] == filename


# --- Test 2: API Endpoint with Mocking ---
async def test_ingest_txt_endpoint():
    """
    Tests the /api/ingest endpoint with a .txt file.
    Mocks the Pinecone call to avoid external dependencies.
    """
    # @patch is a decorator from unittest.mock to replace objects with mocks
    # Here, it replaces 'Pinecone.from_texts' in the 'index' module.
    with patch("index.Pinecone.from_texts") as mock_from_texts:
        mock_from_texts.return_value = MagicMock()

        # httpx.AsyncClient with ASGITransport allows to make requests to our FastAPI app
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Prepare a fake file for upload
            file_content = b"This is a test text file."
            files = {"file": ("test.txt", file_content, "text/plain")}

            response = await client.post("/api/ingest", files=files)

        # Assertions
        assert response.status_code == 200
        response_json = response.json()
        assert (
            response_json["message"] == "File ingested and vectors stored successfully."
        )
        assert response_json["file_name"] == "test.txt"
        assert response_json["vector_count"] > 0

        # Verify that our mock was called, confirming the logic ran
        mock_from_texts.assert_called_once()


async def test_health_check_endpoint():
    """Tests the /api/health endpoint for a successful response."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "Backend is running!"}
