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
    ├── nginx.Dockerfile       # Nginx reverse proxy Dockerfile
    ├── nginx.conf            # Nginx configuration
    └── start.sh              # Backend startup script
```

## Implementation Plan

### Phase 1: Setup & Environment Configuration ✅

- [x] Create pure devenv development environment
- [x] Create directory structure
- [x] Create requirements.txt with necessary dependencies
- [x] Set up Docker configuration with Nginx reverse proxy

### Phase 2: Web Interface ✅

- [x] Create Vue.js chat interface
- [x] Implement Gruvbox theme
- [x] Add responsive design
- [x] Add real-time chat features
- [x] Implement Markdown rendering with marked.js
- [x] Add Gruvbox-themed Markdown styling

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
- [x] Configure Nginx reverse proxy for API endpoints (see docker/nginx.conf for /api/ proxy configuration)

### Phase 6: Docker Deployment ✅

- [x] Create Docker Compose configuration
- [x] Create Dockerfiles for backend and Nginx
- [x] Configure Nginx reverse proxy
- [x] Add NVIDIA CUDA support configuration
- [x] Add AMD ROCm support configuration
- [x] Implement GPU detection and setup commands
- [x] Test Docker deployment
- [x] Add container health checks

### Phase 7: Testing & Refinement ✅

- [x] Test document ingestion process
- [x] Test the RAG pipeline with sample questions
- [x] Test API endpoints
- [x] Test Docker deployment
- [x] Test GPU configurations
- [x] Refine prompt templates and retrieval parameters based on results
- [x] Verify Markdown formatting in responses

### Phase 8: Documentation & Final Setup ✅

- [x] Update directory structure documentation
- [x] Document Docker deployment setup
- [x] Add GPU support documentation
- [x] Document Markdown styling configurations
- [x] Complete API endpoints documentation
- [x] Create example questions and expected answers
- [x] Add troubleshooting guide

## Development Instructions

### Local Development

1. Install Nix and direnv
1. Run `direnv allow` to set up the environment
1. Add CV and skill markdown files to directories
1. Process documents: `python -m src.scripts.ingest_data`
1. Start the local development server: `python -m src.api.main`

### Container Deployment

First, check your GPU support:

```bash
just check-gpu
```

Then deploy based on your hardware:

```bash
# For NVIDIA GPUs:
just up-cuda

# For AMD GPUs:
just up-rocm

# For CPU only:
just up
```

Finally, open [http://localhost:8181](http://localhost:8181) in your browser
