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

RAG_PROMPT_TEMPLATE = """
You are an expert assistant helping answer questions about Olaf Krasicki Freund's CV and professional experience. Always present Olaf as a DevOps and SRE professional. Use ONLY the provided context sections from the CV and the skills documentation (from the skills_md folder) to answer the user's question. Do not make up, summarize, or infer any information that is not explicitly present in the context.

- Always include exact names, dates, job titles, company names, and skill names as they appear in the context. Never omit or paraphrase these details.
- If the answer is found in multiple sections (including both CV and skills_md), synthesize information from all relevant sections, especially sections mentioning Cloud and cloud  infrastruture, but always quote names, dates, titles, and skills exactly as in the context.
- Prefer recent experience and highlight the most relevant skills and technologies.
- If a section header is provided (e.g., '## Professional Experience' or a skill name from skills_md), use it to guide your answer.
- Format all answers to highlight Olaf's DevOps and SRE expertise and values.
- If you do not know the answer based on the provided context, say "I don't know based on the provided CV and skills documentation."
- At the end of your answer, provide a short tip for the user on how to ask for more information. For example: "Tip: You can ask about specific roles, skills, or time periods for more detailed answers."

Context:
{context}

User Question:
{question}

Answer:
"""


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
            search_kwargs={"k": 7}  # Retrieve top 7 most relevant chunks for broader context
        )
        
        # Initialize Ollama model
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Using Ollama LLM base URL: {ollama_base_url}")
        
        llm = OllamaLLM(
            model="llama3",
            temperature=0.0,  # Set to 0.0 for maximum factuality
            base_url=ollama_base_url,
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_PROMPT_TEMPLATE),
            ("human", "{question}")
        ])
        
        def format_context_docs(docs):
            if not docs:
                return "No relevant context found."
            try:
                if isinstance(docs, list) and all(hasattr(doc, 'page_content') for doc in docs):
                    # Log the retrieved context for debugging
                    print("\n--- Retrieved context for query ---")
                    for doc in docs:
                        print(doc.page_content)
                    print("--- End of context ---\n")
                    return "\n\n".join(doc.page_content for doc in docs)
                elif isinstance(docs, str):
                    print(f"\n--- Retrieved context (str) ---\n{docs}\n--- End of context ---\n")
                    return docs
                else:
                    return str(docs)
            except Exception as e:
                print(f"Error formatting context: {e}")
                return "Error retrieving context."
        
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