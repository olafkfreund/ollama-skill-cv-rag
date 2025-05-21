# Personal Skills RAG System with Ollama

This project implements a Retrieval Augmented Generation (RAG) system using Ollama, LangChain, and FastAPI. It allows people to ask questions about your skills and experience, with responses based on your CV and markdown files containing skill descriptions. The system features a modern Vue.js chat interface with a Gruvbox theme and can be run either locally or using Docker.

## 🚀 New Features

- **GPU Acceleration**: Support for NVIDIA CUDA and AMD ROCm GPUs for faster inference
- **Markdown Formatting**: Enhanced response readability with proper Markdown formatting
- **Automatic GPU Detection**: Smart detection and configuration of available GPU hardware
- **Flexible Deployment**: Choose between CPU, NVIDIA, or AMD GPU modes
- **Gruvbox Theme**: Consistent dark theme throughout the interface
- **Caddy Server**: Modern, automatic HTTPS with Caddy reverse proxy
- **Profile Picture Support**: Personal branding with profile picture integration

## Project Overview

The system works by:

1. Loading your CV and skill description markdown files

2. Splitting the documents into manageable chunks

3. Creating embeddings for these chunks using Ollama

4. Storing these embeddings in a vector database (FAISS)

5. When a question is asked, retrieving relevant context from the vector database

6. Using Ollama to generate an answer based on the retrieved context, formatted in Markdown

## Features

- Local execution using Ollama models

- GPU acceleration support (NVIDIA CUDA and AMD ROCm)

- RAG system for accurate, context-based answers

- FastAPI backend for efficient API performance

- Vue.js frontend with Gruvbox theme and Markdown support

- Caddy reverse proxy with automatic HTTPS

- Pure devenv development environment (no flakes)

- Automatic document processing and embedding generation

- Docker support for easy deployment

- Smart GPU detection and configuration

- Profile picture integration for personal branding

## Directory Structure

```plaintext
ollama-rag/
├── devenv.nix                   # Development environment configuration 
├── devenv.yaml                  # Additional devenv configuration
├── docker-compose.yml           # Base Docker configuration
├── docker-compose.cuda.yml      # NVIDIA GPU support configuration
├── docker-compose.rocm.yml      # AMD GPU support configuration
├── requirements.txt             # Python dependencies
├── PROJECT_PLAN.md              # Project planning and progress
├── assets/                      # Static assets
│   └── profile_pictures.jpg     # Profile picture for the chat interface
├── data/                        # Data directory
│   ├── cv/                      # Place your CV files here
│   ├── skills_md/               # Place markdown files about your skills here
│   └── vectorstore/             # Vector database storage
├── src/                         # Source code
│   ├── api/                     # API code
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI application
│   ├── core/                    # Core RAG logic
│   │   ├── __init__.py
│   │   └── rag_pipeline.py      # RAG pipeline implementation
│   └── scripts/                 # Utility scripts
│       ├── __init__.py
│       └── ingest_data.py       # Script to ingest and process data
├── static/                      # Frontend assets
│   └── index.html               # Vue.js chat interface
├── docs/                        # Documentation
│   └── GPU_SUPPORT.md           # GPU configuration guide
└── docker/                      # Docker configuration
    ├── backend.Dockerfile       # Backend service Dockerfile
    ├── caddy.Dockerfile         # Caddy reverse proxy Dockerfile
    ├── Caddyfile                # Caddy configuration
    └── start.sh                 # Backend startup script
```

## Setup Instructions

### Development Environment

1. Install Nix and direnv if not already installed:

   ```bash
   # For Nix
   sh <(curl -L https://nixos.org/nix/install) --daemon

   # For direnv
   nix-env -i direnv
   ```

2. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ollama-rag
   ```

3. Enable direnv:

   ```bash
   direnv allow
   ```

### Local Development

1. Place your CV and skill files in the appropriate directories:

   - Add CV files to `data/cv/`

   - Add skill descriptions to `data/skills_md/`

2. Process your documents:

   ```bash
   python -m src.scripts.ingest_data
   ```

3. Start the development server:

   ```bash
   python -m src.api.main
   ```

4. Visit [http://localhost:8000](http://localhost:8000) in your browser

### Production Deployment

1. Ensure Docker and Docker Compose are installed

2. Check your GPU support:

   ```bash
   just check-gpu
   ```

3. Deploy based on your hardware:

   ```bash
   # For NVIDIA GPUs:
   just up-cuda

   # For AMD GPUs:
   just up-rocm

   # For CPU only:
   just up
   ```

4. Visit [http://localhost:8181](http://localhost:8181) in your browser

## Usage

### Starting the System

Choose the appropriate command based on your hardware:

```bash
# Check GPU support
just check-gpu

# Start with NVIDIA GPU support
just up-cuda

# Start with AMD GPU support
just up-rocm

# Start with CPU only
just up
```

The system will auto-configure based on your hardware and start all necessary services.

### Using the Chat Interface

The chat interface now supports full Markdown formatting in responses:

- Headers for clear section organization

- Code blocks for technical content

- Lists for structured information

- Tables for organized data

- Blockquotes for important notes

- Bold and italic text for emphasis

### API Endpoints

- `GET /`: Serves the Vue.js chat interface with Markdown support

- `POST /api/ask`: Main endpoint for questions and answers

- `GET /api/health`: Health check endpoint

- `GET /docs`: API documentation (Swagger UI)

## Response Format

Responses are formatted in Markdown for better readability:

```markdown
## Topic
Description of the topic

### Subtopic
- List item 1
- List item 2

> Important note or highlight

\`\`\`python
# Code example
def example():
    return "Hello World"
\`\`\`

For more information, see: [link](#)
```

## Container Architecture

The Docker deployment consists of:

- Backend service container with FastAPI

- Caddy reverse proxy for routing and automatic HTTPS

- Optional GPU support configuration

- Automatic hardware detection

- Health monitoring

- Volume mounts for persistence

## Customization

### Changing Profile Information

1. **Profile Picture**:

   - Replace the file at `assets/profile_pictures.jpg` with your own profile picture

   - The recommended image size is 180x180 pixels

   - The image will be automatically styled with a circular crop and subtle shadow

2. **Changing Display Name**:

   - Open `static/index.html`

   - Locate the div with the name (around line 150)

   - Change the text "Olaf K-Freund" to your name

     ```html
     <div style="font-size:1.2rem; color:#bdae93; margin-top:0.5rem; font-weight:bold;">Your Name</div>
     ```

### Domain and SSL Configuration

1. **Changing Domain**:

   - Open `docker/Caddyfile`

   - Replace `home.freundcloud.com` with your domain name

     ```caddy
     your-domain.com {
         # ...existing configuration...
     }
     ```

   - Update the `DOMAIN` environment variable in `docker-compose.yml`:

     ```yaml
     environment:
       - DOMAIN=your-domain.com
     ```

2. **SSL Certificate**:

   - Caddy handles SSL certificates automatically

   - Make sure your domain's DNS points to your server

   - Caddy will automatically obtain and renew certificates from Let's Encrypt

   - For development, Caddy generates self-signed certificates

   - To use a custom certificate:

     ```caddy
     your-domain.com {
         tls /path/to/cert.pem /path/to/key.pem
         # ...rest of configuration...
     }
     ```

After making these changes:

1. Rebuild the containers:

   ```bash
   docker compose down && docker compose up --build -d
   ```

2. Clear your browser cache if the changes don't appear immediately

## Accessing the System

You can access the chat interface in two ways:

- **Locally (HTTP):**

  - Visit [http://localhost:80](http://localhost:80) in your browser for local development and testing.

- **Public (HTTPS):**

  - Visit [https://home.freundcloud.com](https://home.freundcloud.com) for secure, public access with automatic SSL via Caddy.

Both endpoints are available simultaneously for flexible development and deployment.

## Using the API with curl

You can interact with the API directly using `curl` for testing or integration:

### Health Check

```bash
curl http://localhost:80/api/health
curl https://home.freundcloud.com/api/health -k
```

### Ask a Question

```bash
curl -X POST http://localhost:80/api/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "What are your main skills?"}'

curl -X POST https://home.freundcloud.com/api/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "What are your main skills?"}' -k
```

The response will be in the following format:

```json
{
  "status": "success",
  "data": {
    "question": "What are your main skills?",
    "answer": "...markdown-formatted answer..."
  },
  "message": "Answer generated successfully."
}
```

## How to Use This Codebase for Your Own CV/Skills

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd ollama-rag
   ```

2. **Replace Profile Picture:**

   - Place your own image at `assets/profile_pictures.jpg` (recommended size: 180x180px).

3. **Add Your CV and Skills:**

   - Place your CV files in `data/cv/`

   - Place your skill description markdown files in `data/skills_md/`

4. **(Optional) Change Display Name:**

   - Edit `static/index.html` and update the name in the profile section.

5. **(Optional) Change Domain:**

   - Edit `docker/Caddyfile` and `docker-compose.yml` to use your own domain.

   - Update DNS to point to your server.

6. **Process Your Documents:**

   ```bash
   python -m src.scripts.ingest_data
   ```

7. **Start the System:**

   - For local development:

     ```bash
     python -m src.api.main
     # or use Docker Compose for full stack
     docker compose up --build -d
     ```

   - For production, use the appropriate `just up`, `just up-cuda`, or `just up-rocm` command.

8. **Access the Interface:**

   - Local: [http://localhost:80](http://localhost:80)

   - Public: [https://your-domain.com](https://your-domain.com)

## What Needs to Be Changed for Your Own Use

- **Profile Picture:** Replace `assets/profile_pictures.jpg`.

- **CV and Skills:** Add your own files to `data/cv/` and `data/skills_md/`.

- **Display Name:** Edit in `static/index.html`.

- **Domain Name:** Update in `docker/Caddyfile`, `docker-compose.yml`, and DNS.

- **(Optional) Custom SSL:** See Caddyfile section for using your own certificates.

## Documentation

- [GPU Support Guide](docs/GPU_SUPPORT.md): Detailed GPU configuration instructions

- API Documentation: Available at `/docs` endpoint

- [Project Plan](PROJECT_PLAN.md): Implementation details and progress

## Support and Issues

If you encounter any issues:

1. Check the GPU support with `just check-gpu`

2. Verify your Docker installation

3. Check the logs with `just logs`

4. Consult the [GPU Support Guide](docs/GPU_SUPPORT.md)
