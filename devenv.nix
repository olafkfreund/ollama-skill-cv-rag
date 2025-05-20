# Development environment for RAG system
{pkgs, ...}: {
  name = "rag-environment";

  # Python development environment
  languages.python = {
    enable = true;
    version = "3.11";
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };

  # Required packages
  packages = with pkgs; [
    git
    gh
    gnumake
    curl
    jq
    # python tools (uncomment if needed for troubleshooting)
    # black
    # pylint
    # python311Packages.pip
    # python311Packages.setuptools
    # python311Packages.wheel
    # pandoc
    # texlive.combined.scheme-full
  ];

  # Environment variables
  env = {
    # PYTHONPATH = toString ./.;
    OLLAMA_HOST = "http://localhost:11434";
  };

  # Shell hook for developer guidance
  enterShell = ''
    echo "🚀 Welcome to the RAG development environment!"
    echo ""
    echo "Available commands:"
    echo "  ingest       # Process documents (python -m src.scripts.ingest_data)"
    echo "  start-api    # Start the API server (python -m src.api.main)"
    echo ""
    echo "Health check:"
    echo "  curl http://localhost:8000/health"
    echo ""
  '';

  # Scripts available in the environment
  scripts = {
    ingest.exec = "python -m src.scripts.ingest_data";
    start-api.exec = "python -m src.api.main";
  };

  # Process management
  processes.api.exec = "python -m src.api.main";
}
