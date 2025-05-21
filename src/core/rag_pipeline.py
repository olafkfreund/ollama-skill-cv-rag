#!/usr/bin/env python
"""
RAG pipeline implementation for retrieving context and generating answers.
"""

import os
from pathlib import Path
from typing import Dict, Any

from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores.faiss import FAISS
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore" / "faiss_index"


def load_vector_store():
    """
    Load the vector store from disk with dangerous deserialization enabled.
    
    Returns:
        FAISS: The loaded vector store
    """
    print("Loading embeddings model...")
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Debug the connection to Ollama
    print(f"Using Ollama base URL: {ollama_base_url}")
    
    # Use a custom embeddings class to handle the input correctly
    class SafeOllamaEmbeddings(OllamaEmbeddings):
        def embed_documents(self, texts):
            # Ensure texts are always strings
            clean_texts = [str(text) if not isinstance(text, str) else text for text in texts]
            return super().embed_documents(clean_texts)
            
        def embed_query(self, text):
            # Ensure query is always a string
            clean_text = str(text) if not isinstance(text, str) else text
            return super().embed_query(clean_text)
    
    # Create embeddings with our safer wrapper
    embeddings = SafeOllamaEmbeddings(
        model="llama3",
        base_url=ollama_base_url,
    )
    
    print(f"Loading vector store from: {VECTORSTORE_DIR}")
    
    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found at {VECTORSTORE_DIR}. "
            "Please run the ingestion script first: python -m src.scripts.ingest_data"
        )
    
    return FAISS.load_local(str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True)


def create_rag_chain() -> Runnable:
    """
    Create the RAG chain for retrieving context and generating answers.
    
    Returns:
        Runnable: The RAG chain
    """
    try:
        # Load vector store and create retriever
        vector_store = load_vector_store()
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
        )
        
        # Initialize Ollama model
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Using Ollama LLM base URL: {ollama_base_url}")
        
        llm = OllamaLLM(
            model="llama3",
            temperature=0.1,  # Low temperature for more factual responses
            base_url=ollama_base_url,
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant answering questions about Olaf Krasicki Freund's professional experience, 
skills, and technical knowledge. Format your responses using Markdown for better readability.

When answering questions:
1. Prioritize information from CV sections when discussing work history and core skills
2. Use skills documentation for detailed technical explanations
3. Combine both sources when appropriate to provide comprehensive answers

Format your responses following these guidelines:
## For Main Topics (like Work Experience, Technical Skills)
### For Subtopics (like specific roles or technologies)
* Use bullet points for lists
* Use `code` for technical terms, commands, or tools
* Use **bold** for companies and job titles
* Use > for important achievements or key responsibilities
* Use --- for separating major sections
* Use Markdown tables for structured data
* Include appropriate line breaks between sections

When discussing technical topics:
- Link related skills together
- Provide context for technical terms
- Highlight practical experience with technologies
- Include relevant certifications or qualifications

If the information asked for is not in the context, respond with: 
> "I don't have enough information about that in Olaf's CV or skill descriptions."

Remember to structure your response with clear sections and proper formatting for optimal readability.

Context:
{context}"""),
            ("human", "{question}")
        ])
        
        # Define a simple function to format the context
        def format_context_docs(docs):
            # Handle the case where docs might be unexpected format
            if not docs:
                return "No relevant context found."
                
            try:
                if isinstance(docs, list) and all(hasattr(doc, 'page_content') for doc in docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                elif isinstance(docs, str):
                    return docs
                else:
                    # Attempt to convert whatever we got to a string
                    return str(docs)
            except Exception as e:
                print(f"Error formatting context: {e}")
                return "Error retrieving context."
        
        # Build the RAG chain using LCEL with proper input transformations and error handling
        rag_chain = (
            {"context": retriever | format_context_docs, "question": lambda x: x["question"]} 
            | prompt 
            | llm 
            | StrOutputParser()
        )
        
        return rag_chain
    except Exception as e:
        print(f"Error creating RAG chain: {e}")
        raise


def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer a question using the RAG pipeline.
    
    Args:
        question (str): The question to answer
        
    Returns:
        Dict[str, Any]: A dictionary containing the question and answer
    """
    try:
        print(f"Processing question: {question}")
        
        # Create RAG chain if not already created
        rag_chain = create_rag_chain()
        
        # Generate answer
        answer = rag_chain.invoke({"question": question})
        
        return {
            "question": question,
            "answer": answer,
            "success": True
        }
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        # Provide a more user-friendly error message
        error_message = "I encountered an issue processing your question. This could be due to a temporary problem with the language model or the retrieval system."
        if "validation error" in str(e).lower():
            print("Validation error detected, likely an issue with the embeddings API")
            error_message = "There was an issue with the underlying embeddings model. The system administrators have been notified."
        
        return {
            "question": question,
            "answer": error_message,
            "success": False,
            "error_details": str(e)  # Include the technical details for debugging
        }