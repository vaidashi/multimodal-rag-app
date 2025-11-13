"""Script to upload the evaluation document to the backend."""

import requests

# Create the evaluation document content
eval_doc_content = """
Project Alpha: A technical overview.
The primary objective of Project Alpha is to develop a new customer relationship management (CRM) platform.
This platform will be built using modern technologies. The backend will be implemented in Python,
while the frontend will utilize the React library. The project is managed by Sarah, a senior engineer.
The main stakeholder and client for this project is Globex Corporation, who have provided detailed requirements.
"""

filename = "evaluation_doc.txt"

# Save to a file
with open(filename, "w") as f:
    f.write(eval_doc_content.strip())

print(f"Created {filename}")

# Upload to the backend API
api_url = "http://localhost:8000/api/ingest"

with open(filename, "rb") as f:
    files = {"file": (filename, f, "text/plain")}
    response = requests.post(api_url, files=files)

if response.status_code == 200:
    print(f"✅ Successfully uploaded {filename} to the backend!")
    print(f"Response: {response.json()}")
else:
    print(f"❌ Failed to upload. Status: {response.status_code}")
    print(f"Response: {response.text}")
