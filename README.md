# Multi-Modal RAG Application

This was an effort to build a MVP-ready Retrieval-Augmented Generation (RAG) system with multi-modal support, featuring a Next.js frontend and FastAPI backend. Upload PDFs and images, extract knowledge graphs, and interact with your documents through an intelligent Q&A interface with speech capabilities.

## 🌟 Features

- **📄 Multi-Modal Document Processing**
  - PDF upload with text and image extraction
  - Direct image upload with vision-based description
  - Automatic document chunking and vectorization

- **🧠 Advanced RAG Capabilities**
  - Vector-based semantic search with Pinecone
  - Document isolation with metadata filtering
  - Knowledge graph extraction from documents
  - Agentic routing between specialized tools

- **🗣️ Speech Integration**
  - Speech-to-text input (Web Speech API)
  - Text-to-speech output (OpenAI TTS)
  - Natural conversational interface

- **📊 Evaluation Framework**
  - RAGAS-based RAG evaluation
  - Metrics: Context Precision, Recall, Faithfulness, Answer Relevancy

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │────────▶│    Backend      │
│   (Next.js)     │         │   (FastAPI)     │
│   Port: 3000    │         │   Port: 8000    │
└─────────────────┘         └─────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             ┌──────────┐    ┌──────────┐   ┌──────────┐
             │ OpenAI   │    │ Pinecone │   │ LangChain│
             │   API    │    │  Vector  │   │   Agent  │
             └──────────┘    └──────────┘   └──────────┘
```

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites

- Docker Desktop installed
- OpenAI API key
- Pinecone API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd multimodal-rag-app
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=sk-...
   PINECONE_API_KEY=pcsk_...
   ```

3. **Build and run**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Commands

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Rebuild after changes
docker compose up --build
```

See [DOCKER_README.md](./DOCKER_README.md) for detailed Docker documentation.

## 💻 Local Development Setup (Non-Docker)

### Prerequisites

- Python 3.12+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (recommended for faster Python package installation)

### Backend Setup

#### Option 1: Using uv (Recommended - Faster)

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or: pip install uv
   ```

2. **Navigate to API directory and sync dependencies**
   ```bash
   cd api
   uv sync
   ```

3. **Create `.env` file in the `api` directory**
   ```env
   OPENAI_API_KEY=sk-...
   PINECONE_API_KEY=pcsk_...
   ```

4. **Setup Pinecone index**
   ```bash
   uv run python setup_pinecone.py
   ```

5. **Run the backend using root package.json script**
   ```bash
   cd ..  # Return to root
   npm run dev:backend
   ```

#### Option 2: Using pip

1. **Navigate to API directory**
   ```bash
   cd api
   ```

2. **Create Python virtual environment**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

4. **Create `.env` file in the `api` directory**
   ```env
   OPENAI_API_KEY=sk-...
   PINECONE_API_KEY=pcsk_...
   ```

5. **Setup Pinecone index**
   ```bash
   python setup_pinecone.py
   ```

6. **Run the backend using root package.json script**
   ```bash
   cd ..  # Return to root
   npm run dev:backend
   ```
   
   Or run directly:
   ```bash
   cd api
   uvicorn index:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to app directory**
   ```bash
   cd app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create `.env.local` file**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server using root package.json script**
   ```bash
   cd ..  # Return to root
   npm run dev:frontend
   ```
   
   Or run directly:
   ```bash
   cd app
   npm run dev
   ```

5. **Access the app**
   - Open http://localhost:3000

### Running Both Services (Recommended)

From the root directory, install dependencies and run both services in parallel:

```bash
# Install root dependencies (npm-run-all)
npm install

# Run both frontend and backend simultaneously
npm run dev
```

This uses the root `package.json` scripts:
- `npm run dev` - Runs both services in parallel
- `npm run dev:frontend` - Runs only the frontend
- `npm run dev:backend` - Runs only the backend

## 🔑 OpenAI API Setup

This application uses the following OpenAI models. Ensure your API key has access to these models:

### Required Models

1. **GPT-4o** (`gpt-4o`)
   - Used for: Main chat responses, vision analysis, knowledge graph extraction
   - Enable at: https://platform.openai.com/settings/organization/limits
   - Required tier: Tier 1+

2. **GPT-3.5 Turbo** (`gpt-3.5-turbo`)
   - Used for: Text summarization, document isolation
   - Enable at: https://platform.openai.com/settings/organization/limits
   - Available on all tiers

3. **Text Embedding 3 Small** (`text-embedding-3-small`)
   - Used for: Document vectorization, semantic search
   - Dimension: 1536
   - Available on all tiers

4. **TTS-1** (`tts-1`)
   - Used for: Text-to-speech output
   - Voice: `alloy`
   - Available on all tiers

### API Key Setup

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add billing information if not already done
4. Check model access at https://platform.openai.com/settings/organization/limits
5. For GPT-4o access, you may need to upgrade to a paid tier

## 📊 Running Tests

### Backend Tests

```bash
cd api

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd app

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 🧪 RAG Evaluation

Evaluate RAG performance using RAGAS metrics:

```bash
cd api

# Upload evaluation document (first time only)
python upload_eval_doc.py

# Run evaluation
python evaluate_rag.py
```

Metrics evaluated:
- **Context Precision**: Relevance of retrieved context
- **Context Recall**: Completeness of retrieved context
- **Faithfulness**: Factual consistency with context
- **Answer Relevancy**: Relevance of answer to question

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 16.0.1
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: React
- **Speech**: Web Speech API

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12
- **LLM Framework**: LangChain
- **Vector Database**: Pinecone
- **AI Models**: OpenAI (GPT-4o, GPT-3.5, Embeddings, TTS)
- **PDF Processing**: PyMuPDF
- **Image Processing**: Pillow
- **Graph Processing**: NetworkX

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Package Management**: npm (frontend), pip (backend)

## 📁 Project Structure

```
multimodal-rag-app/
├── api/                      # Backend (FastAPI)
│   ├── index.py             # Main API routes
│   ├── models.py            # Pydantic models
│   ├── pinecone_store.py    # Custom vector store
│   ├── evaluate_rag.py      # RAG evaluation script
│   ├── setup_pinecone.py    # Pinecone index setup
│   ├── tests/               # Backend tests
│   └── pyproject.toml       # Python dependencies
├── app/                      # Frontend (Next.js)
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx     # Main UI
│   │       └── layout.tsx   # App layout
│   ├── package.json         # Node dependencies
│   └── next.config.ts       # Next.js config
├── Dockerfile               # Backend container
├── Dockerfile.frontend      # Frontend container
├── docker-compose.yml       # Multi-container orchestration
├── .dockerignore           # Docker build exclusions
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

**Backend** (`.env` or in `docker-compose.yml`):
```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
```

**Frontend** (`.env.local` or in `docker-compose.yml`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Pinecone Configuration

The application uses:
- **Index Name**: `multimodal-docs`
- **Dimension**: 1536 (for `text-embedding-3-small`)
- **Metric**: Cosine similarity
- **Cloud**: AWS
- **Region**: us-east-1

Modify in `api/setup_pinecone.py` if needed.

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Verify environment variables
docker compose config

# Rebuild from scratch
docker compose down
docker compose build --no-cache backend
docker compose up backend
```

### Frontend can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check NEXT_PUBLIC_API_URL in docker-compose.yml
docker compose config | grep NEXT_PUBLIC_API_URL
```

### OpenAI API errors
- Verify API key is correct
- Check model access at https://platform.openai.com/settings/organization/limits
- Ensure billing is set up
- For GPT-4o, upgrade to Tier 1+ if needed

### Pinecone errors
- Verify API key is correct
- Run `python api/setup_pinecone.py` to create index
- Check index exists at https://app.pinecone.io

## 📝 API Endpoints

### Document Management
- `POST /api/upload-pdf` - Upload and process PDF
- `POST /api/upload-image` - Upload and process image
- `DELETE /api/delete-doc/{doc_id}` - Delete document
- `GET /api/list-docs` - List all documents

### RAG & Query
- `POST /api/query` - Query documents
- `POST /api/isolate-doc` - Isolate specific document
- `POST /api/extract-graph` - Extract knowledge graph

### Speech
- `POST /api/text-to-speech` - Convert text to speech

### Utility
- `GET /api/health` - Health check

Full API documentation: http://localhost:8000/docs

## 🚢 Production Deployment

### Option 1: Docker on VPS
Deploy to DigitalOcean, Linode, or any VPS:
```bash
# On your server
git clone <repo>
cd multimodal-rag-app
docker compose up -d
```

### Option 2: Separate Deployments
- **Frontend**: Deploy to Vercel (see `vercel.json`)
- **Backend**: Deploy to Render, Railway, or Fly.io

### Option 3: Cloud Container Services
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

See [DOCKER_README.md](./DOCKER_README.md) for more deployment options.

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues and questions, please open a GitHub issue.
