#!/usr/bin/env python
"""
FastAPI application for the RAG system.
"""

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

try:
    import uvicorn
except ImportError:
    uvicorn = None

from src.core.rag_pipeline import answer_question


def create_response(status: str, data: Any, message: str) -> Dict[str, Any]:
    """
    Create a standardized API response.
    
    Args:
        status (str): Response status ("success" or "error")
        data (Any): Response data
        message (str): Response message
    
    Returns:
        Dict[str, Any]: Formatted response dictionary
    """
    return {
        "status": status,
        "data": data,
        "message": message
    }


# Initialize FastAPI app
app = FastAPI(
    title="Personal Skills RAG System",
    description="A RAG system that answers questions about my skills and experience",
    version="1.0.0"
)

# Define base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates_dir = BASE_DIR / "templates"
static_dir = BASE_DIR / "static"
assets_dir = BASE_DIR / "assets"

# Static files and templates
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Only mount assets if the directory exists
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
else:
    print(f"Warning: Assets directory '{assets_dir}' does not exist, skipping mount")
templates = Jinja2Templates(directory=str(templates_dir))

# Add CORS middleware to allow requests from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request model
class QuestionRequest(BaseModel):
    query: str


# Define response model
class AnswerResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
async def read_root(request: Request):
    """Root endpoint that returns the web interface."""
    try:
        # Try to use the templates directory first
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"Error rendering template: {e}")
        # Fallback to returning the static index.html file
        return FileResponse(static_dir / "index.html")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Endpoint to ask a question about skills and experience.
    
    Args:
        request (QuestionRequest): The question request
        
    Returns:
        JSONResponse: The standardized API response
    """
    try:
        if not request.query or request.query.strip() == "":
            return JSONResponse(
                status_code=200,  # Always return 200 for frontend compatibility
                content=create_response(
                    status="error",
                    data={},
                    message="Query cannot be empty"
                )
            )
            
        print(f"API received question: {request.query}")
        
        # Get the answer from the RAG pipeline
        result = answer_question(request.query)
        
        if not result["success"]:
            # Check if we have error details for debugging
            error_details = result.get("error_details", "Unknown error")
            print(f"Error details: {error_details}")
            
            return JSONResponse(
                status_code=200,  # Always return 200 for frontend compatibility
                content=create_response(
                    status="error",
                    data={
                        "question": result["question"],
                        "answer": result["answer"]
                    },
                    message=result["answer"]
                )
            )
            
        print(f"Successfully generated answer of length: {len(result['answer'])}")
        
        return JSONResponse(
            status_code=200,
            content=create_response(
                status="success",
                data={
                    "question": result["question"],
                    "answer": result["answer"]
                },
                message="Answer generated successfully"
            )
        )
    except Exception as e:
        print(f"Unexpected API error: {str(e)}")
        return JSONResponse(
            status_code=200,  # Always return 200 for frontend compatibility
            content=create_response(
                status="error",
                data={},
                message=f"An unexpected error occurred: {str(e)}"
            )
        )


@app.post("/chat")
async def chat(request: Request):
    """
    Endpoint for the chat interface.
    
    Args:
        request (Request): The request object
        
    Returns:
        JSONResponse: The response with the answer
    """
    try:
        # Parse the request body
        body = await request.json()
        query = body.get("query", "")
        
        if not query or query.strip() == "":
            return JSONResponse(
                content={"response": "Please enter a question."}
            )
            
        # Process the query through the RAG pipeline
        result = answer_question(query)
        
        if not result["success"]:
            return JSONResponse(
                content={"response": result["answer"] or "I couldn't process that query."}
            )
            
        return JSONResponse(
            content={"response": result["answer"]}
        )
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return JSONResponse(
            content={"response": f"An error occurred: {str(e)}"}
        )




# Optional: Add a simple HTML interface
try:
    # Create directory for static files and templates if they don't exist
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    static_dir = BASE_DIR / "static"
    templates_dir = BASE_DIR / "templates"
    assets_dir = BASE_DIR / "assets"
    
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create a simple HTML interface
    with open(templates_dir / "index.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Skills RAG</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            background-color: #f9f9f9;
        }
        .chat-messages {
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #eee;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #e3f2fd;
            color: #0d47a1;
            text-align: right;
        }
        .ai-message {
            background-color: #f1f8e9;
            color: #33691e;
            text-align: left;
        }
        .chat-input {
            display: flex;
        }
        input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background-color: #4caf50;
            color: white;
            border: none;
            border-radius: 4px;
            margin-left: 10px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Personal Skills RAG</h1>
    <p>Ask questions about my skills and experience:</p>
    
    <div class="chat-container">
        <div id="messages" class="chat-messages"></div>
        <div class="chat-input">
            <input 
                type="text" 
                id="question" 
                placeholder="What would you like to know about my skills?"
                onkeydown="if(event.key === 'Enter') sendQuestion();"
            >
            <button onclick="sendQuestion()">Ask</button>
        </div>
    </div>

    <script>
        async function sendQuestion() {
            const questionInput = document.getElementById('question');
            const messagesContainer = document.getElementById('messages');
            const question = questionInput.value.trim();
            
            if (!question) return;
            
            // Add user message to chat
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.textContent = question;
            messagesContainer.appendChild(userMessage);
            
            // Clear input
            questionInput.value = '';
            
            // Create AI message placeholder
            const aiMessage = document.createElement('div');
            aiMessage.className = 'message ai-message';
            aiMessage.textContent = 'Thinking...';
            messagesContainer.appendChild(aiMessage);
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: question }),
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    aiMessage.textContent = data.answer;
                } else {
                    aiMessage.textContent = `Error: ${data.detail || 'Something went wrong'}`;
                }
            } catch (error) {
                aiMessage.textContent = `Error: ${error.message}`;
            }
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    </script>
</body>
</html>
        """)
    
    # Mount static files and templates
    templates = Jinja2Templates(directory=str(templates_dir))
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    # Add a route for the HTML interface
    @app.get("/chat", include_in_schema=False)
    async def chat_interface(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
        
except Exception as e:
    print(f"Warning: Could not set up the HTML interface: {e}")


def start():
    """
    Function to start the server when running the module directly.
    
    Usage:
        python -m src.api.main
    """
    if uvicorn is None:
        raise ImportError("uvicorn is not installed. Please install it to run the server.")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )


if __name__ == "__main__":
    start()
