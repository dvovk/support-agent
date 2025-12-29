import os
import json
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import TextLoader, DirectoryLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings # Updated import
from langchain_community.vectorstores import Chroma # This might also need to be updated to langchain_chroma
from langchain_core.documents import Document

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
PERSIST_DIRECTORY = "chroma_db"  # Directory to store the ChromaDB
DISCORD_CLEANED_JSON = "discord_cleaned.json"
GITHUB_REPO_DIR = "data/erigon"  # Set to the cloned Erigon repository

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

def load_github_data(repo_path: Path) -> List[Document]:
    """Loads documents from the cloned Erigon repository, with specific inclusions and exclusions."""
    if not repo_path.is_dir():
        logger.warning(f"GitHub repository directory not found: {repo_path}. Skipping GitHub data ingestion.")
        return []

    # File types to include for Erigon
    file_globs = ["**/*.md", "**/*.txt", "**/*.go", "**/*.sh", "**/*.toml", "**/*.proto"]
    
    all_docs = []
    for g in file_globs:
        try:
            loader = DirectoryLoader(
                str(repo_path),
                glob=g,
                loader_cls=TextLoader,
                recursive=True,
                show_progress=True,
                loader_kwargs={'encoding': 'utf-8'}
            )
            loaded_docs = loader.load()
            all_docs.extend(loaded_docs)
        except Exception as e:
            logger.error(f"Error loading files with glob {g}: {e}")

    logger.info(f"Loaded a total of {len(all_docs)} documents from {repo_path} before filtering.")

    # Directories to exclude
    excluded_dirs = [str(repo_path / 'build'), str(repo_path / 'testdata')]

    final_docs = []
    for doc in all_docs:
        source_path = doc.metadata.get('source', '')
        if not any(Path(source_path).is_relative_to(excluded_dir) for excluded_dir in excluded_dirs):
            doc.metadata["type"] = "github_code_doc"
            final_docs.append(doc)

    logger.info(f"Filtered documents down to {len(final_docs)} after removing excluded directories.")
    return final_docs

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
    github_path = Path(GITHUB_REPO_DIR)
    
    # --- GitHub Ingestion ---
    github_docs = load_github_data(github_path)
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
