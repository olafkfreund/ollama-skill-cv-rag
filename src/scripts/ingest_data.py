#!/usr/bin/env python
"""
Script to ingest data from CV and markdown files and create a vector store.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CV_DIR = BASE_DIR / "data" / "cv"
SKILLS_DIR = BASE_DIR / "data" / "skills_md"
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore"

def get_relative_path(file_path: Path, base_dir: Path) -> str:
    """Get the relative path from base_dir to file_path."""
    try:
        return str(file_path.relative_to(base_dir))
    except ValueError:
        return str(file_path)

def load_markdown_with_metadata(file_path: Path, base_dir: Path) -> List[Document]:
    """
    Load a markdown file with proper metadata and header-based splitting.
    
    Args:
        file_path (Path): Path to the markdown file
        base_dir (Path): Base directory for relative path calculation
        
    Returns:
        List[Document]: List of document chunks with metadata
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define headers to split on
    headers_to_split_on = [
        ("#", "header1"),
        ("##", "header2"),
        ("###", "header3"),
    ]
    
    # Split text based on headers
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    
    # Get header-based splits
    docs = markdown_splitter.split_text(content)
    
    # Add file metadata to each document
    relative_path = get_relative_path(file_path, base_dir)
    category = file_path.parent.name
    
    for doc in docs:
        doc.metadata.update({
            "source": relative_path,
            "category": category,
            "file_type": "markdown",
            "full_path": str(file_path)
        })
    
    return docs

def chunk_markdown_by_section(md_text: str) -> List[Dict[str, Any]]:
    """
    Chunk markdown text by section headers (##) and attach section header as metadata.
    Args:
        md_text: The markdown text to chunk.
    Returns:
        List of dicts with 'content' and 'metadata' (section header).
    """
    sections = re.split(r'(^## .+$)', md_text, flags=re.MULTILINE)
    chunks = []
    for i in range(1, len(sections), 2):
        header = sections[i].strip()
        content = sections[i+1].strip()
        chunks.append({'content': f'{header}\n{content}', 'metadata': {'section': header}})
    return chunks

def load_documents() -> List[Document]:
    """
    Load documents from CV and skills markdown directories.
    
    Returns:
        List[Document]: A list of loaded documents
    """
    documents = []

    # Load CV documents
    if CV_DIR.exists():
        # Load PDFs
        for pdf_file in CV_DIR.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf_file))
            pdf_docs = loader.load()
            
            # Add metadata
            for doc in pdf_docs:
                doc.metadata.update({
                    "source": get_relative_path(pdf_file, BASE_DIR),
                    "category": "cv",
                    "file_type": "pdf"
                })
            documents.extend(pdf_docs)

        # Load CV markdown
        for md_file in CV_DIR.glob("*.md"):
            docs = load_markdown_with_metadata(md_file, BASE_DIR)
            documents.extend(docs)

    # Load skills markdown documents recursively
    if SKILLS_DIR.exists():
        for md_file in SKILLS_DIR.rglob("*.md"):
            docs = load_markdown_with_metadata(md_file, BASE_DIR)
            documents.extend(docs)

    if not documents:
        print("No documents found in CV or skills directories.")
    else:
        print(f"Loaded {len(documents)} documents:")
        # Print summary of loaded documents by category
        categories = {}
        for doc in documents:
            cat = doc.metadata.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in categories.items():
            print(f"  - {cat}: {count} documents")

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
        separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    return split_docs

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
    model_name = os.environ.get("MODEL_NAME", "llama3")
    
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
        model=model_name,
        base_url=ollama_base_url
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