# Personal Skills RAG System with Ollama

This project implements a Retrieval Augmented Generation (RAG) system using Ollama, LangChain, and FastAPI. It enables users to ask questions about your skills and experience, with responses grounded in your CV and markdown files containing skill descriptions. The system features a modern Vue.js chat interface with a Gruvbox theme and can be run locally or with Docker.

## 🚀 Features (2025)

- **GPU Acceleration:** Supports NVIDIA CUDA and AMD ROCm GPUs for faster inference
- **Markdown Formatting:** Enhanced response readability with proper Markdown formatting
- **Automatic GPU Detection:** Smart detection and configuration of available GPU hardware
- **Flexible Deployment:** Choose between CPU, NVIDIA, or AMD GPU modes
- **Gruvbox Theme:** Consistent dark theme throughout the interface
- **Caddy Server:** Automatic HTTPS with Caddy reverse proxy
- **Profile Picture Support:** Personal branding with profile picture integration
- **Modern RAG Pipeline:** Uses FAISS vector store, Ollama embeddings, and LangChain for robust retrieval
- **OpenAPI Documentation:** All API endpoints are documented and discoverable
- **Modular Architecture:** Easily extend with new skills, markdown files, or CVs

## 🏗️ Architecture

- **Backend:** FastAPI, LangChain, Ollama, FAISS
- **Frontend:** Vue.js 3, Gruvbox Material Dark theme
- **Reverse Proxy:** Caddy (automatic HTTPS)
- **Containerization:** Docker, Docker Compose (with CUDA/ROCm support)
- **Development Environment:** NixOS devenv for reproducible builds

## 📦 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Ollama (local LLM runner)
- Node.js & npm (for frontend development)
- Nix (for reproducible development environment)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/olafkfreund/ollama-skill-cv-rag.git
cd ollama-skill-cv-rag
```

### 2. Setup Development Environment (Recommended)

```bash
devenv shell
```

### 3. Build and Run with Docker

- **CPU only:**

  ```bash
  docker-compose up --build
  ```

- **NVIDIA GPU:**

  ```bash
  docker-compose -f docker-compose.yml -f docker-compose.cuda.yml up --build
  ```

- **AMD GPU:**

  ```bash
  docker-compose -f docker-compose.yml -f docker-compose.rocm.yml up --build
  ```

### 4. Manual Backend/Frontend Start (Dev)

- **Backend:**

  ```bash
  cd src/backend
  uvicorn main:app --reload
  ```

- **Frontend:**

  ```bash
  cd src/frontend
  npm install
  npm run dev
  ```

## 📝 Usage

- Access the chat UI at `http://localhost:3000` (or as configured)
- Ask questions about your skills, experience, or any indexed markdown content
- Responses are grounded in your CV and skill markdown files

## 🗂️ Adding Skills & CVs

- Place markdown skill files in `data/skills_md/pages/`
- Update your CV in the appropriate directory and metadata
- Run the data ingestion script:

  ```bash
  python src/scripts/ingest_data.py
  ```

## 🗂️ File Overview

- `src/backend/` — FastAPI backend, RAG pipeline, document processing, and API logic
- `src/frontend/` — Vue.js 3 frontend chat UI (Gruvbox theme)
- `data/skills_md/pages/` — Markdown files describing skills/topics
- `data/cv/` — CV files to be indexed
- `src/scripts/ingest_data.py` — Data ingestion script for skills and CVs
- `docker-compose.yml` — Main Docker Compose configuration
- `docker-compose.cuda.yml` — NVIDIA GPU support
- `docker-compose.rocm.yml` — AMD GPU support
- `Caddyfile` — Caddy reverse proxy configuration
- `Makefile` — Common development and build tasks
- `.env.example` — Example environment variables
- `PROJECT_PLAN.md` — Project goals, architecture, and onboarding
- `README.md` — Main documentation

## 🔒 Security & Best Practices

- All user input is validated and sanitized
- CORS is configured for frontend/backend separation
- Secrets and credentials are managed via environment variables
- Docker images use multi-stage builds for minimal size and security

## 🧪 Testing

- Run backend tests:

  ```bash
  python3 run_tests.py
  ```

- Frontend tests:

  ```bash
  cd src/frontend
  npm run test
  ```

## 🧑‍💻 Development Workflow

- Always start with `devenv shell` for NixOS reproducibility
- Use the Makefile and scripts for common tasks
- Refer to `PROJECT_PLAN.md` and this README for up-to-date goals and onboarding

## 🩺 Health Checks & Monitoring

- Caddy and backend expose health endpoints for readiness/liveness
- Logs are output to stdout/stderr for container monitoring

## 📚 Documentation

- All API endpoints are documented via OpenAPI (Swagger UI at `/api/docs`)
- See `PROJECT_PLAN.md` for architecture and onboarding
- Environment variables are documented in `.env.example`

## 🧩 Extending the System

- Add new markdown files for additional skills or topics
- Integrate new LLMs via Ollama configuration
- Customize the frontend theme in `src/frontend` (Gruvbox colors)

## Latest Updates

### CV Retrieval Enhancement

- The system now ensures that Olaf Freund's CV is shown when a user query is about the CV.
- CV documents are processed with explicit metadata: `type: "cv"`, `owner: "Olaf Freund"`, `title: "Olaf Freund CV"`.
- Retrieval logic prioritizes or filters for documents with this metadata when the query is about the CV.
- To process and index your CV, use:

```python
cv_metadata = {
    "type": "cv",
    "owner": "Olaf Freund",
    "title": "Olaf Freund CV"
}
cv_documents = await process_document(cv_content, cv_metadata)
# Add cv_documents to your vector store as usual
```

- For more details, see the Copilot Instructions and code comments.

## 🆘 Troubleshooting

- See the FAQ and troubleshooting sections in this README
- For NixOS issues, always run `devenv shell` before any dev commands
- For GPU issues, check Docker Compose overrides and driver installation

## 🤝 Contributing

- See `CONTRIBUTING.md` for guidelines
- PRs and issues are welcome!

## 📄 License

MIT

---

For more details, see the [PROJECT_PLAN.md](./PROJECT_PLAN.md) and in-code documentation.
