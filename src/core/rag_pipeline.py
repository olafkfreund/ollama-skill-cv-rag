#!/usr/bin/env python
"""
RAG pipeline implementation for retrieving context and generating answers.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import re
import aiofiles

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
> "I don't have enough information about that in Olaf's CV or skill descriptions.But if you have a look at https://freundcloud.gitbook.io/devops-examples-from-real-life"

Remember to structure your response with clear sections and proper formatting for optimal readability.
- Always include exact names, dates, job titles, company names, and skill names as they appear in the context. Never omit or paraphrase these details.
- If the answer is found in multiple sections (including both CV and skills_md), synthesize information from all relevant sections, but always quote names, dates, titles, and skills exactly as in the context.
- Prefer recent experience and highlight the most relevant skills and technologies.
- If a section header is provided (e.g., '## Professional Experience' or a skill name from skills_md), use it to guide your answer.
- If the context includes code examples, always include them in your answer using Markdown code blocks.
- Format all answers to highlight Olaf's DevOps and SRE expertise and values.
- If you do not know the answer based on the provided context, say "I don't know based on the provided CV and skills documentation."
- At the end of your answer, provide a short tip for the user on how to ask for more information. For example: "Tip: You can ask about specific roles, skills, time periods, or request code examples for more detailed answers. Try asking: 'Show me a code example for Terraform automation.'or have a look at https://freundcloud.gitbook.io/devops-examples-from-real-life"

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


def is_cv_query(question: str) -> bool:
    """
    Detect if the user query is a request to show the CV or resume.
    Args:
        question (str): The user query
    Returns:
        bool: True if the query is about the CV, False otherwise
    """
    cv_keywords = [
        r"\bcv\b", r"curriculum vitae", r"resume", r"show.*cv", r"show.*resume", r"see.*cv", r"see.*resume",
        r"your cv", r"your resume", r"full cv", r"full resume", r"download.*cv", r"download.*resume"
    ]
    q = question.lower()
    return any(re.search(pattern, q) for pattern in cv_keywords)


def get_full_cv_markdown() -> str:
    """
    Return the full CV markdown as a string.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    cv_path = base_dir / "data" / "cv" / "cv.md"
    if not cv_path.exists():
        return "CV file not found."
    try:
        with open(cv_path, mode="r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read CV file: {e}")
        return "Error reading CV file."


def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer a question using the RAG pipeline, or return the full CV if the query is about the CV.
    Args:
        question (str): The question to answer
    Returns:
        Dict[str, Any]: A dictionary containing the question and answer
    """
    try:
        print(f"Processing question: {question}")
        if is_cv_query(question):
            cv_md = get_full_cv_markdown()
            return {
                "question": question,
                "answer": cv_md,
                "success": True
            }
        rag_chain = create_rag_chain()
        answer = rag_chain.invoke({"question": question})
        return {
            "question": question,
            "answer": answer,
            "success": True
        }
    except Exception as e:
        print(f"Error answering question: {str(e)}")
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


async def list_all_cv_entries() -> str:
    """
    Extract and format all professional experience entries from the CV markdown.
    Returns:
        A Markdown-formatted string listing all professional experience entries.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    cv_path = base_dir / "data" / "cv" / "cv.md"
    if not cv_path.exists():
        return "CV file not found."
    try:
        async with aiofiles.open(cv_path, mode="r", encoding="utf-8") as f:
            cv_markdown = await f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read CV file: {e}")
        return "Error reading CV file."
    # Debug: print the first 500 characters of the CV markdown
    print("[DEBUG] Loaded CV markdown (first 500 chars):", cv_markdown[:500])
    # Extract the Professional Experience section
    match = re.search(r"## Professional Experience(.+?)(\n## |\Z)", cv_markdown, re.DOTALL)
    if not match:
        print("[DEBUG] No professional experience section found in the CV.")
        return "No professional experience section found in the CV."
    section = match.group(1)
    # Debug: print the section
    print("[DEBUG] Professional Experience section (first 500 chars):", section[:500])
    # Ensure all entries start with '###'
    entries = re.findall(r"(### .+?)(?=\n### |\Z)", section, re.DOTALL)
    if not entries:
        print("[DEBUG] No '###' entries found, returning whole section.")
        return f"## Professional Experience\n{section.strip()}"
    formatted = "\n\n".join(entry.strip() for entry in entries)
    print(f"[DEBUG] Found {len(entries)} entries.")
    return f"## Professional Experience\n\n{formatted}"

async def list_cv_section(section_name: str) -> str:
    """
    Extract and format a specific section from the CV markdown.
    Args:
        section_name: The section header to extract (e.g., 'Core Competencies & Technical Skills')
    Returns:
        A Markdown-formatted string of the section, or an error message.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    cv_path = base_dir / "data" / "cv" / "cv.md"
    if not cv_path.exists():
        return f"CV file not found."
    try:
        async with aiofiles.open(cv_path, mode="r", encoding="utf-8") as f:
            cv_markdown = await f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read CV file: {e}")
        return "Error reading CV file."
    # Extract the requested section
    pattern = rf"## {re.escape(section_name)}(.+?)(\n## |\Z)"
    match = re.search(pattern, cv_markdown, re.DOTALL)
    if not match:
        print(f"[DEBUG] No section '{section_name}' found in the CV.")
        return f"No section '{section_name}' found in the CV."
    section = match.group(1)
    return f"## {section_name}\n{section.strip()}"

async def list_cv_full() -> str:
    """
    Return the full CV markdown content.
    Returns:
        The full CV as a Markdown-formatted string, or an error message.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    cv_path = base_dir / "data" / "cv" / "cv.md"
    if not cv_path.exists():
        return "CV file not found."
    try:
        async with aiofiles.open(cv_path, mode="r", encoding="utf-8") as f:
            cv_markdown = await f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read CV file: {e}")
        return "Error reading CV file."
    return cv_markdown

async def generate_response(query: str, context: List[Dict[str, Any]] = None) -> str:
    """
    Generate a response using the RAG pipeline. If the query is for the full CV or a section, return the relevant content.
    Args:
        query: User query
        context: Retrieved documents (optional)
    Returns:
        Generated response
    """
    cv_keywords = [
        "show me your cv", "list all professional experience", "show all cv entries", "full cv", "all roles", "all jobs", "all experience", "cv entries", "cv", "professional experience"
    ]
    section_keywords = [
        "core competencies", "technical skills", "summary", "volunteering", "languages", "interests"
    ]
    q_lower = query.lower()
    if any(k in q_lower for k in cv_keywords):
        # If user asks for the full CV, return all professional experience entries
        return await list_all_cv_entries()
    for section in section_keywords:
        if section in q_lower:
            # Return the requested section
            pretty_section = section.title() if section != "core competencies" else "Core Competencies & Technical Skills"
            return await list_cv_section(pretty_section)
    if "full cv" in q_lower or "entire cv" in q_lower or "complete cv" in q_lower:
        return await list_cv_full()
    # ...existing RAG pipeline code...