# GPU Support

The system can be run with different GPU configurations for Ollama:

## Quick Start

Check your GPU support:
```bash
just check-gpu
```

This will detect your GPU and suggest the appropriate command to use.

## Available GPU Options

### NVIDIA CUDA Support
For systems with NVIDIA GPUs:
```bash
just up-cuda      # Start with NVIDIA GPU support
just build-cuda   # Build with NVIDIA support
just rebuild-cuda # Rebuild and restart with NVIDIA support
```

Requirements:
- NVIDIA GPU
- NVIDIA Container Toolkit installed
- CUDA drivers

### AMD ROCm Support
For systems with AMD GPUs:
```bash
just up-rocm      # Start with AMD GPU support
just build-rocm   # Build with AMD support
just rebuild-rocm # Rebuild and restart with AMD support
```

Requirements:
- AMD GPU
- ROCm stack installed
- ROCm-compatible drivers

### CPU Only / Local Ollama
For systems without GPU or using a local Ollama installation:
```bash
just up           # Start without GPU support
just build        # Build without GPU support
just rebuild      # Rebuild and restart without GPU support
```

## Notes

- When using GPU support, the system will automatically use the appropriate Ollama container (CUDA or ROCm)
- If using a local Ollama installation, ensure it's running before starting the services
- The system will use the same port (11434) regardless of the chosen configuration
- GPU support significantly improves model inference speed

## Troubleshooting

If you encounter issues:

1. Verify GPU support:
   - NVIDIA: `nvidia-smi`
   - AMD: `rocm-smi`

2. Check container toolkit installation:
   - NVIDIA: `docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`
   - ROCm: `docker run --rm --device=/dev/kfd --device=/dev/dri rocm/rocm-terminal rocm-smi`

3. Ensure proper permissions:
   - For ROCm: User should be in 'video' and 'render' groups
   - For NVIDIA: User should be in 'docker' group
