# Design Document: Local-First RAG Support Assistant

## 1. Overview
This document outlines the architecture for a Retrieval-Augmented Generation (RAG) support assistant. The system will run entirely on a local Windows machine, using local data sources, local models, and a local vector database. The goal is to answer user questions by grounding responses in a knowledge base derived from Discord chat history and a GitHub code repository.

## 2. Architecture
The system is composed of two main pipelines: an **Ingestion Pipeline** for indexing data and a **Query Pipeline** for answering questions.

**Text-Based Flowchart:**
```
[Data Sources]      --> [Ingestion Pipeline] --> [Vector Database]
(Discord Export,
 GitHub Repo)

[User Question] --> [Query Pipeline] --> [LLM] --> [Answer & Sources]
                         ^                |
                         |                |
                       [Retriever] <--- [Vector Database]
```

## 3. Component Breakdown

### 3.1. Data Sources
- **Discord History:** A static export of Discord conversations (e.g., in JSON or CSV format).
- **GitHub Repository:** A clone of a public GitHub repository containing code and documentation.

### 3.2. Ingestion Pipeline (The "Indexer")
This is an offline process that prepares the knowledge base.
- **Loader:** Reads files from the data sources (e.g., `.json` files from Discord, `.py`/`.md` files from GitHub).
- **Cleaner:** Performs basic text pre-processing to remove noise (e.g., bot commands, excessive newlines).
- **Chunker:** Splits large documents into smaller, semantically meaningful chunks.
  - **Discord:** Chunks will be based on conversation threads or groups of related messages to maintain context.
  - **Code:** Chunks will be based on functions or classes to keep related code together.
- **Embedder:** Converts each text chunk into a numerical vector embedding.
- **Vector Store:** Stores the embeddings in a database for efficient similarity searching.

### 3.3. Query Pipeline (The "Querier")
This is the online process that runs when a user asks a question.
- **Input:** A user's question (e.g., "How do I fix error X?").
- **Retriever:**
  1. The user's question is converted into an embedding using the same Embedder model.
  2. The Vector Store is searched to find the text chunks with the most similar embeddings (i.e., the most relevant information).
- **Generator:**
  1. A prompt is constructed containing the user's original question and the retrieved text chunks.
  2. This prompt is sent to the local Generation LLM to produce a final, synthesized answer.
- **Output:** The final answer is presented to the user, along with references to the original source documents (e.g., file path or Discord message link) that were used to generate it.

## 4. Technology Stack (MVP)
This stack is chosen for a 100% local, Windows-based setup with no required cloud services or API keys for the core functionality.

- **Operating System:** Windows
- **Language:** Python
- **LLM Serving:** **Ollama**
  - Manages and serves the generation model via a local API.
- **Models:**
  - **Embedding Model:** `all-MiniLM-L6-v2`. Runs locally via the `sentence-transformers` Python library.
  - **Generation Model:** `Llama 3 8B`. Runs locally via **Ollama**.
- **Vector Store:** **ChromaDB**
  - A local, file-based vector database that is easy to set up and use with Python.
- **Key Python Libraries:**
  - `langchain` or `llama-index`: To orchestrate the RAG pipeline.
  - `sentence-transformers`: To load and run the embedding model.
  - `chromadb`: To interact with the vector database.
  - `requests` or `httpx`: To communicate with the local Ollama API endpoint.
