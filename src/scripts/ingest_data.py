#!/usr/bin/env python
"""
Script to ingest data from CV and markdown files and create a vector store.
"""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CV_DIR = BASE_DIR / "data" / "cv"
SKILLS_DIR = BASE_DIR / "data" / "skills_md"
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore"


def load_documents() -> List[Document]:
    """
    Load documents from CV and skills markdown directories.
    
    Returns:
        List[Document]: A list of loaded documents
    """
    documents = []

    # Load CV documents (PDFs and Markdown)
    if CV_DIR.exists():
        for pdf_file in CV_DIR.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf_file))
            documents.extend(loader.load())
        for md_file in CV_DIR.glob("*.md"):
            loader = TextLoader(str(md_file), encoding="utf-8")
            documents.extend(loader.load())

    # Load skill markdown documents
    if SKILLS_DIR.exists():
        for md_file in SKILLS_DIR.glob("*.md"):
            loader = TextLoader(str(md_file), encoding="utf-8")
            documents.extend(loader.load())

    if not documents:
        print("No documents found in CV or skills directories.")
    else:
        print(f"Loaded {len(documents)} documents from CV and skills directories.")

    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval using project-specific parameters.
    
    Args:
        documents (List[Document]): The documents to split
        
    Returns:
        List[Document]: The split documents
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Project standard
        chunk_overlap=50,  # Project standard
        length_function=len,
    )
    return text_splitter.split_documents(documents)


def create_vector_store(documents: List[Document]) -> FAISS:
    """
    Create a vector store from the documents.
    
    Args:
        documents (List[Document]): The documents to add to the vector store
        
    Returns:
        FAISS: The vector store
    """
    print("Initializing Ollama embeddings...")
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Create a safer wrapper for OllamaEmbeddings that ensures proper input format
    class SafeOllamaEmbeddings(OllamaEmbeddings):
        def embed_documents(self, texts):
            # Ensure texts are always strings
            clean_texts = [str(text) if not isinstance(text, str) else text for text in texts]
            return super().embed_documents(clean_texts)
            
        def embed_query(self, text):
            # Ensure query is always a string
            clean_text = str(text) if not isinstance(text, str) else text
            return super().embed_query(clean_text)
    
    # Use the safer wrapper
    embeddings = SafeOllamaEmbeddings(
        model="llama3",
        base_url=ollama_base_url,
    )
    
    print(f"Using Ollama base URL: {ollama_base_url}")
    print(f"Creating vector store with {len(documents)} document chunks...")
    vector_store = FAISS.from_documents(documents, embeddings)
    
    # Create the vectorstore directory if it doesn't exist
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    
    # Save the vector store
    vector_store_path = str(VECTORSTORE_DIR / "faiss_index")
    print(f"Saving vector store to: {vector_store_path}")
    vector_store.save_local(vector_store_path)
    
    return vector_store


def load_vector_store(embeddings: OllamaEmbeddings) -> FAISS:
    """
    Load the FAISS vector store with dangerous deserialization enabled (safe for trusted local files).
    """
    vector_store_path = str(VECTORSTORE_DIR / "faiss_index")
    return FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)


def main():
    """Main function to run the ingestion process."""
    print("Starting document ingestion process...")
    
    # Load documents
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    
    # Split documents
    print("Splitting documents into chunks...")
    split_docs = split_documents(documents)
    print(f"Split into {len(split_docs)} chunks")
    
    # Create and save vector store
    create_vector_store(split_docs)
    
    print("Document ingestion complete!")
    print(f"Vector store saved to: {VECTORSTORE_DIR / 'faiss_index'}")


if __name__ == "__main__":
    main()