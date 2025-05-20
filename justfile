# Justfile for building and running Docker images for the Ollama RAG system

# Default build without GPU support
build:
    docker compose build

# Build with CUDA support
build-cuda:
    docker compose -f docker-compose.yml -f docker-compose.cuda.yml build

# Build with ROCm support
build-rocm:
    docker compose -f docker-compose.yml -f docker-compose.rocm.yml build

# Start services using local Ollama (default)
up:
    docker compose up -d

# Start services with CUDA Ollama
up-cuda:
    docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d

# Start services with ROCm Ollama
up-rocm:
    docker compose -f docker-compose.yml -f docker-compose.rocm.yml up -d

# Stop all running services
down:
    docker compose down

# Show logs for all services
logs:
    docker compose logs -f

# Check GPU support and suggest command
check-gpu:
    #!/usr/bin/env sh
    if command -v nvidia-smi >/dev/null 2>&1; then
        echo "NVIDIA GPU detected, use 'just up-cuda'"
    elif [ -d "/dev/dri" ] && [ -d "/dev/kfd" ]; then
        echo "AMD GPU detected, use 'just up-rocm'"
    else
        echo "No GPU detected, use 'just up' (local Ollama)"
    fi

# Set up SSL certificates
setup-ssl:
    ./scripts/init-letsencrypt.sh

# Start services with SSL
up-ssl:
    docker compose up -d

# View Caddy logs
caddy-logs:
    docker compose logs -f caddy

# Check Caddy status
caddy-status:
    docker compose exec caddy caddy status

# Rebuild and restart with local Ollama
rebuild:
    just down
    just build
    just up

# Rebuild and restart with CUDA
rebuild-cuda:
    just down
    just build-cuda
    just up-cuda

# Rebuild and restart with ROCm
rebuild-rocm:
    just down
    just build-rocm
    just up-rocm
