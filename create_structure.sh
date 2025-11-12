#!/bin/bash

echo "🚀 Creating AI Agent Platform structure..."

# API Gateway (Golang)
echo "📁 Creating API structure..."
mkdir -p api/cmd/server
mkdir -p api/internal/{handlers,middleware,models,services,repository}
mkdir -p api/pkg/{redis,grpc,utils}

# Agent Services (Python)
echo "📁 Creating Agents structure..."
mkdir -p agents/{core,graphs,chains,tools,prompts}

# RAG System
echo "📁 Creating RAG structure..."
mkdir -p rag/{ingestion,retrieval,vectordb,embeddings}

# Model Service
echo "📁 Creating Models structure..."
mkdir -p models/providers

# Infrastructure
echo "📁 Creating Infrastructure structure..."
mkdir -p redis/init-scripts
mkdir -p nginx/ssl
mkdir -p monitoring/{prometheus,grafana/dashboards}

# Data directories
echo "📁 Creating Data directories..."
mkdir -p data/{documents,vectordb,uploads}

# Others
mkdir -p {scripts,docs/api}
mkdir -p tests/{api,agents,integration}

# Root config files
echo "📄 Creating root config files..."
touch {docker-compose.yml,docker-compose.dev.yml,docker-compose.prod.yml}
touch {.env.example,.gitignore,README.md}

# API files
echo "📄 Creating API files..."
touch api/cmd/server/main.go
touch api/{go.mod,Dockerfile,.dockerignore}

# Agent files
echo "📄 Creating Agent files..."
touch agents/{app.py,requirements.txt,Dockerfile,.dockerignore}
touch agents/core/{__init__,agent_executor,memory,tools}.py
touch agents/graphs/{__init__,rag_graph,multi_agent_graph,supervisor_graph}.py
touch agents/chains/{__init__,qa_chain,summarization_chain,routing_chain}.py
touch agents/tools/{__init__,web_search,calculator,database_tool}.py
touch agents/prompts/{__init__,system_prompts,few_shot_examples}.py

# RAG files
echo "📄 Creating RAG files..."
touch rag/{app.py,requirements.txt,Dockerfile,.dockerignore}
touch rag/ingestion/{__init__,loader,chunker,preprocessor}.py
touch rag/retrieval/{__init__,vector_store,reranker,hybrid_search}.py
touch rag/vectordb/{__init__,qdrant_client,chroma_client,weaviate_client}.py
touch rag/embeddings/{__init__,embedding_service}.py

# Model files
echo "📄 Creating Model files..."
touch models/{app.py,requirements.txt,Dockerfile,.dockerignore}
touch models/{router,cache,fallback}.py
touch models/providers/{__init__,openai_provider,gemini_provider,anthropic_provider,local_model_provider}.py

# Config files
echo "📄 Creating config files..."
touch redis/redis.conf
touch nginx/nginx.conf
touch monitoring/prometheus/prometheus.yml
touch monitoring/docker-compose.monitoring.yml

# Scripts
echo "📄 Creating scripts..."
touch scripts/{setup.sh,migrate.sh,backup.sh}
chmod +x scripts/*.sh

# Documentation
touch docs/{architecture.md,deployment.md}

echo ""
echo "✅ Structure created successfully!"
echo "📂 Project location: $(pwd)"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  code .  # Open in VS Code"
echo ""

# Create basic .gitignore
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
*.log

# Docker
*.pid

# Data
data/documents/*
data/vectordb/*
data/uploads/*
!data/documents/.gitkeep
!data/vectordb/.gitkeep
!data/uploads/.gitkeep

# OS
.DS_Store
Thumbs.db
GITIGNORE

# Create .gitkeep for empty data directories
touch data/documents/.gitkeep
touch data/vectordb/.gitkeep
touch data/uploads/.gitkeep

# Create basic README
cat > README.md << 'README'
# AI Agent Platform

Enterprise-grade AI Agent platform with RAG, multiple LLM providers, and microservices architecture.

## Architecture

- **API Gateway**: Golang - High-performance REST API
- **Agent Service**: Python - LangChain/LangGraph orchestration
- **RAG Service**: Python - Document retrieval and embedding
- **Model Service**: Python - Multi-provider LLM routing
- **Redis**: Caching and session management
- **Vector DB**: Qdrant for semantic search

## Quick Start
```bash
# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Services

- API Gateway: http://localhost:8080
- Agent Service: http://localhost:8000
- RAG Service: http://localhost:8001
- Model Service: http://localhost:8002
- Redis: localhost:6379
- Qdrant: http://localhost:6333

## Development

See `docs/` for detailed documentation.
README

echo "📝 Created .gitignore and README.md"
echo "🎉 All done!"

