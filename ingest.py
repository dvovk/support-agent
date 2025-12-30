import os
import json
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
DISCORD_CLEANED_JSON = "discord_cleaned.json"
GITHUB_CLEANED_JSON = "github_cleaned.json"

# --- Helper Functions ---

def load_discord_data(file_path: Path) -> List[Document]:
    """Loads cleaned Discord messages from a JSON file."""
    if not file_path.exists():
        logger.warning(f"Discord cleaned data file not found: {file_path}. Skipping Discord data ingestion.")
        return []

    loader = JSONLoader(
        file_path=str(file_path),
        jq_schema='.[].content',
        text_content=False
    )
    
    documents = loader.load()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, doc in enumerate(documents):
        if i < len(data):
            doc.metadata = {
                "author": data[i].get("author", "unknown"),
                "timestamp": data[i].get("timestamp", "unknown"),
                "source": data[i].get("source", str(file_path.name)),
                "type": "discord_message"
            }
        else:
            doc.metadata = {"source": str(file_path.name), "type": "discord_message"}
            
    logger.info(f"Loaded {len(documents)} documents from {file_path}.")
    return documents

def load_structured_github_data(file_path: Path) -> List[Document]:
    """Loads structured GitHub data from a JSON file."""
    if not file_path.exists():
        logger.warning(f"GitHub cleaned data file not found: {file_path}. Skipping GitHub data ingestion.")
        return []

    loader = JSONLoader(
        file_path=str(file_path),
        jq_schema='.[].content',
        text_content=False
    )
    
    documents = loader.load()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, doc in enumerate(documents):
        if i < len(data):
            doc.metadata = {
                "source": data[i].get("source", str(file_path.name)),
                "type": "github_code_doc"
            }
        else:
            doc.metadata = {"source": str(file_path.name), "type": "github_code_doc"}
            
    logger.info(f"Loaded {len(documents)} documents from {file_path}.")
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def main():
    """Main function to orchestrate data ingestion into separate databases."""
    logger.info("Starting data ingestion process...")

    # Define paths
    discord_json_path = Path(DISCORD_CLEANED_JSON)
    github_json_path = Path(GITHUB_CLEANED_JSON)
    
    # --- GitHub Ingestion ---
    github_docs = load_structured_github_data(github_json_path)
    if github_docs:
        github_chunks = split_documents(github_docs)
        logger.info("Initializing GitHub embedding model and ChromaDB...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        github_vectorstore = Chroma.from_documents(
            documents=github_chunks,
            embedding=embeddings,
            persist_directory="chroma_db_github"
        )
        github_vectorstore.persist()
        logger.info("GitHub ChromaDB ingestion complete.")
    else:
        logger.warning("No GitHub documents found to ingest.")

    # --- Discord Ingestion ---
    discord_docs = load_discord_data(discord_json_path)
    if discord_docs:
        discord_chunks = split_documents(discord_docs)
        logger.info("Initializing Discord embedding model and ChromaDB...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        discord_vectorstore = Chroma.from_documents(
            documents=discord_chunks,
            embedding=embeddings,
            persist_directory="chroma_db_discord"
        )
        discord_vectorstore.persist()
        logger.info("Discord ChromaDB ingestion complete.")
    else:
        logger.warning("No Discord documents found to ingest.")

if __name__ == "__main__":
    main()
