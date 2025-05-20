# Copilot Instructions for Ollama RAG System

# Workflow

## High-Level Problem Solving Strategy

1. Understand the problem deeply. Carefully read the issue and think critically about what is required.
2. Investigate the codebase. Explore relevant files, search for key functions, and gather context.
3. Develop a clear, step-by-step plan. Break down the fix into manageable, incremental steps.
4. Implement the fix incrementally. Make small, testable code changes.
5. Debug as needed. Use debugging techniques to isolate and resolve issues.
6. Test frequently. Run tests after each change to verify correctness.
7. Iterate until the root cause is fixed and all tests pass.
8. Reflect and validate comprehensively. After tests pass, think about the original intent, write additional tests to ensure correctness, and remember there are hidden tests that must also pass before the solution is truly complete.

Refer to the detailed sections below for more information on each step.

## 1. Deeply Understand the Problem
Carefully read the issue and think hard about a plan to solve it before coding.

## 2. Codebase Investigation
- Explore relevant files and directories.
- Search for key functions, classes, or variables related to the issue.
- Read and understand relevant code snippets.
- Identify the root cause of the problem.
- Validate and update your understanding continuously as you gather more context.

## 3. Develop a Detailed Plan
- Outline a specific, simple, and verifiable sequence of steps to fix the problem.
- Break down the fix into small, incremental changes.

## 4. Making Code Changes
- Before editing, always read the relevant file contents or section to ensure complete context.
- If a patch is not applied correctly, attempt to reapply it.
- Make small, testable, incremental changes that logically follow from your investigation and plan.

## 5. Debugging
- Make code changes only if you have high confidence they can solve the problem
- When debugging, try to determine the root cause rather than addressing symptoms
- Debug for as long as needed to identify the root cause and identify a fix
- Use print statements, logs, or temporary code to inspect program state, including descriptive statements or error messages to understand what's happening
- To test hypotheses, you can also add test statements or functions
- Revisit your assumptions if unexpected behavior occurs.

## 6. Testing
- Run tests frequently using `!python3 run_tests.py` (or equivalent).
- After each change, verify correctness by running relevant tests.
- If tests fail, analyze failures and revise your patch.
- Write additional tests if needed to capture important behaviors or edge cases.
- Ensure all tests pass before finalizing.

## 7. Final Verification
- Confirm the root cause is fixed.
- Review your solution for logic correctness and robustness.
- Iterate until you are extremely confident the fix is complete and all tests pass.

## 8. Final Reflection and Additional Testing
- Reflect carefully on the original intent of the user and the problem statement.
- Think about potential edge cases or scenarios that may not be covered by existing tests.
- Write additional tests that would need to pass to fully validate the correctness of your solution.
- Run these new tests and ensure they all pass.
- Be aware that there are additional hidden tests that must also pass for the solution to be successful.
- Do not assume the task is complete just because the visible tests pass; continue refining until you are confident the fix is robust and comprehensive.


## Project Overview
This is a Retrieval Augmented Generation (RAG) system using Ollama, LangChain, and FastAPI. The system processes CV and markdown files to answer questions about skills and experience through a Vue.js chat interface with Gruvbox theme.

## Key Technologies
- Python 3.x
- FastAPI
- LangChain
- Ollama
- Vue.js
- Docker/Docker Compose
- Nginx
- FAISS vector store
- devenv (Nix-based development environment)

## Code Style Guidelines

### Python
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use async/await for all I/O operations
- Organize imports in the following order:
  1. Standard library
  2. Third-party packages
  3. Local modules
- Use docstrings for all public functions and classes

### Vue.js
- Follow Vue.js 3 composition API patterns
- Use Gruvbox theme colors consistently
- Maintain responsive design principles
- Keep components modular and reusable

### Docker
- Use multi-stage builds where appropriate
- Follow best practices for container security
- Keep image sizes minimal

## Project Structure Patterns

### API Endpoints
- Base URL: `/api`
- RESTful naming conventions
- Include OpenAPI/Swagger documentation
- Response format:
```json
{
  "status": "success|error",
  "data": {},
  "message": "string"
}
```

### RAG Pipeline
- Document chunking size: 500 tokens
- Use Ollama embeddings
- FAISS vector store configuration
- Top k documents: 3
- Temperature: 0.7

## Documentation Requirements
- Add docstrings to all Python functions
- Maintain API documentation in OpenAPI format
- Keep README.md and PROJECT_PLAN.md up to date
- Document environment variables

## Error Handling
- Use custom exception classes
- Log errors with appropriate levels
- Return meaningful error messages
- Implement graceful fallbacks

## Testing Guidelines
- Write unit tests for core functionality
- Use pytest for Python tests
- Include integration tests for RAG pipeline
- Test Docker deployment

## Security Considerations
- Validate all user input
- Sanitize file inputs
- Use proper CORS configuration
- Follow Docker security best practices

## Performance Optimization
- Cache embeddings where possible
- Optimize vector search parameters
- Use connection pooling for databases
- Implement proper Docker layer caching

## Deployment Practices
- Use health checks
- Implement graceful shutdown
- Set up proper logging
- Configure resource limits

## Environment Variables
Expected environment variables:
```env
OLLAMA_BASE_URL=http://localhost:11434
VECTOR_STORE_PATH=./data/vectorstore
MODEL_NAME=llama2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_DOCS=3
TEMPERATURE=0.7
```

## Common Functions

### Document Processing
```python
async def process_document(
    content: str,
    metadata: Dict[str, Any]
) -> List[Document]:
    """
    Process a document for the RAG pipeline.
    
    Args:
        content: Raw document content
        metadata: Document metadata
        
    Returns:
        List of processed documents
    """
    pass
```

### RAG Pipeline
```python
async def generate_response(
    query: str,
    context: List[Document]
) -> str:
    """
    Generate a response using the RAG pipeline.
    
    Args:
        query: User query
        context: Retrieved documents
        
    Returns:
        Generated response
    """
    pass
```

### API Response
```python
def create_response(
    status: str,
    data: Any,
    message: str
) -> Dict[str, Any]:
    """
    Create a standardized API response.
    
    Args:
        status: Response status
        data: Response data
        message: Response message
        
    Returns:
        Formatted response dictionary
    """
    pass
```

## Notes for AI Assistance
- Maintain type safety
- Follow existing patterns in the codebase
- Preserve the Gruvbox theme in UI components
- Keep Docker configurations consistent
- Ensure async/await is used appropriately
- Maintain proper error handling patterns
- Follow the established project structure
- Use devenv for development environment setup
- You are an agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved.
-If you are not sure about file content or codebase structure pertaining to the user’s request, use your tools to read files and gather the relevant information: do NOT guess or make up an answer.
