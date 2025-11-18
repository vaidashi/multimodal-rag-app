# Multi-Modal RAG Application - Docker Setup

A containerized multi-modal RAG (Retrieval-Augmented Generation) application with Next.js frontend and FastAPI backend.

## Prerequisites

- Docker Desktop installed
- Docker Compose installed
- OpenAI API key
- Pinecone API key

## Quick Start

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 2. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs

## Docker Commands

### Start Services
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Status
```bash
# View running containers
docker-compose ps

# View resource usage
docker stats
```

## Development Workflow

### Hot Reload

The backend supports hot reload for development:

```bash
# Edit api/index.py and changes will reload automatically
```

For frontend changes, rebuild:

```bash
docker-compose up --build frontend
```

### Run Backend Only
```bash
docker-compose up backend
```

### Run Frontend Only
```bash
docker-compose up frontend
```

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose config

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache backend
docker-compose up backend
```

### Frontend Can't Connect to Backend
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check network
docker network ls
docker network inspect multimodal-rag-app_app-network
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Example: "3001:3000" instead of "3000:3000"
```

### Clean Everything
```bash
# Remove all containers, networks, and images
docker-compose down
docker system prune -a
```

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │────────▶│    Backend      │
│   (Next.js)     │         │   (FastAPI)     │
│   Port: 3000    │         │   Port: 8000    │
└─────────────────┘         └─────────────────┘
        │                           │
        │                           │
        ▼                           ▼
   User Browser              External APIs
                          (OpenAI, Pinecone)
```

## Production Deployment

For production, consider:

1. Use environment-specific `.env` files
2. Enable HTTPS with reverse proxy (nginx)
3. Set up persistent volumes for data
4. Configure proper logging and monitoring
5. Use Docker secrets for sensitive data

## Features

- ✅ PDF document processing with text and image extraction
- ✅ Image upload and vision-based description
- ✅ Speech-to-text (Web Speech API)
- ✅ Text-to-speech (OpenAI TTS)
- ✅ Knowledge graph extraction
- ✅ Vector-based document retrieval
- ✅ Agentic routing between tools

## Tech Stack

**Frontend:**
- Next.js 16
- React
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI
- LangChain
- OpenAI API
- Pinecone Vector Database
- PyMuPDF

## License

MIT
