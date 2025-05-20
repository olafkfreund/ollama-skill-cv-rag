# Ollama RAG System Project Plan

## Project Overview

This project creates a Retrieval Augmented Generation (RAG) system using Ollama, allowing users to ask questions about your skills and experience. The system uses your CV and markdown files as the knowledge base, retrieving relevant information to generate accurate answers.

## Key Features

- 🚀 **GPU Acceleration**: Support for NVIDIA CUDA and AMD ROCm GPUs
- 📝 **Markdown Support**: Enhanced response formatting with Markdown
- 🎨 **Gruvbox Theme**: Consistent dark theme throughout the UI
- 🔄 **Flexible Deployment**: Run with or without GPU support
- 🤖 **Advanced RAG Pipeline**: Optimized for accurate responses
- 🔒 **Secure Docker Setup**: Following best practices for container security
- 🔐 **HTTPS by Default**: Automatic HTTPS with Caddy server
- 🖼️ **Profile Integration**: Personal branding with profile picture

## Project Structure

```plaintext
ollama-rag/
├── devenv.nix                 # Development environment configuration
├── devenv.yaml                # Additional devenv configuration
├── docker-compose.yml         # Base Docker configuration
├── docker-compose.cuda.yml    # NVIDIA GPU support configuration
├── docker-compose.rocm.yml    # AMD GPU support configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── PROJECT_PLAN.md           # This file
├── assets/
│   └── profile_pictures.jpg  # Profile picture for chat interface
├── data/
│   ├── cv/                    # Directory for your CV file
│   ├── skills_md/             # Directory for skill description markdown files
│   └── vectorstore/           # Directory for storing the vector database
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   └── rag_pipeline.py    # RAG pipeline implementation
│   └── scripts/
│       ├── __init__.py
│       └── ingest_data.py     # Script to process documents and create vector store
├── static/
│   └── index.html            # Vue.js chat interface with Gruvbox theme
├── docs/
│   └── GPU_SUPPORT.md        # GPU configuration documentation
└── docker/
    ├── backend.Dockerfile     # Backend service Dockerfile
    ├── caddy.Dockerfile      # Caddy reverse proxy Dockerfile
    ├── Caddyfile             # Caddy server configuration
    └── start.sh              # Backend startup script
```

## Implementation Plan

### Phase 1: Setup & Environment Configuration ✅

- [x] Create pure devenv development environment
- [x] Create directory structure
- [x] Create requirements.txt with necessary dependencies
- [x] Set up Docker configuration with reverse proxy

### Phase 2: Web Interface ✅

- [x] Create Vue.js chat interface
- [x] Implement Gruvbox theme
- [x] Add responsive design
- [x] Add real-time chat features
- [x] Implement Markdown rendering with marked.js
- [x] Add Gruvbox-themed Markdown styling
- [x] Add profile picture support
- [x] Configure Caddy for static file serving

### Phase 3: Data Processing Pipeline ✅

- [x] Implement document loading functionality for CV and markdown files
- [x] Implement text splitting to create chunks of appropriate size (chunk_size=500, chunk_overlap=50)
- [x] Set up Ollama embeddings generation (using OllamaEmbeddings in ingest_data.py)
- [x] Create FAISS vector store and persistence mechanism (see ingest_data.py)

### Phase 4: RAG Pipeline Implementation ✅

- [x] Create functionality to load the vector store (see load_vector_store in rag_pipeline.py)
- [x] Initialize Ollama LLM for text generation (see Ollama initialization in rag_pipeline.py)
- [x] Design and implement prompt template for answering questions (see ChatPromptTemplate in rag_pipeline.py)
- [x] Build the complete RAG chain using LangChain Expression Language (LCEL) (see rag_chain in rag_pipeline.py)
- [x] Enhance prompt template for Markdown output

### Phase 5: API Development ✅

- [x] Create FastAPI application with chat endpoint (see main.py for /ask endpoint)
- [x] Integrate the RAG pipeline with the API (see main.py for integration with answer_question from rag_pipeline.py)
- [x] Add error handling and logging (see exception handling and logging in main.py)
- [x] Configure Caddy reverse proxy for API endpoints (see docker/Caddyfile for /api/ proxy configuration)

### Phase 6: Docker Deployment ✅

- [x] Create Docker Compose configuration
- [x] Create Dockerfiles for backend and Caddy
- [x] Configure Caddy reverse proxy with automatic HTTPS
- [x] Add NVIDIA CUDA support configuration
- [x] Add AMD ROCm support configuration
- [x] Implement GPU detection and setup commands
- [x] Add assets handling in Caddy configuration
- [x] Test Docker deployment

### Phase 7: Enhancements and Optimizations ✅

- [x] Implement proper static file serving with Caddy
- [x] Add profile picture support in the UI
- [x] Configure automatic HTTPS with Caddy
- [x] Optimize Docker container configurations
- [x] Improve error handling and logging
- [x] Add comprehensive documentation
