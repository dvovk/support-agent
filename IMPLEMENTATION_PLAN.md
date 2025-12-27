# Implementation Plan: Local-First RAG Support Assistant

This document provides a step-by-step guide to building the RAG support assistant on a Windows machine.

---

## Phase 1: Setup and Data Ingestion

### Step 1: Prepare the Windows Environment
First, ensure your system has the necessary base tools.

1.  **Install Python:** If you don't have it, install Python 3.9+ from the [official Python website](https://www.python.org/downloads/) or the Microsoft Store. Ensure you check the box `Add Python to PATH` during installation.
2.  **Install Git:** Download and install [Git for Windows](https://git-scm.com/download/win). This will be needed to clone your source code repository.
3.  **Verify Installation:** Open a new PowerShell or Command Prompt terminal and run `python --version` and `git --version` to ensure they are installed correctly.

### Step 2: Install and Set Up Ollama
This will be our local server for the main language model.

1.  **Download Ollama:** Go to the [Ollama website](https://ollama.com/) and download the installer for Windows.
2.  **Install Ollama:** Run the installer. It will set up Ollama as a background service.
3.  **Pull the LLM (Ollama Refresher):**
    *   Open a PowerShell or Command Prompt terminal.
    *   Run the following command to download the Llama 3 8B model:
      ```bash
      ollama pull llama3
      ```
    *   You can see all models you have downloaded by running `ollama list`.
    *   Ollama runs a server in the background automatically. By default, it's available at `http://localhost:11434`. You can test this by visiting the URL in your browser.

### Step 3: Set Up the Python Project
Let's create our project folder and set up a virtual environment.

1.  Create a project folder, e.g., `support-assistant`.
2.  Open a terminal inside this folder.
3.  Create a Python virtual environment:
    ```bash
    python -m venv .venv
    ```
4.  Activate the virtual environment:
    ```bash
    .\.venv\Scripts\activate
    ```
    Your terminal prompt should now be prefixed with `(.venv)`.
5.  Install the necessary Python libraries:
    ```bash
    pip install langchain langchain_community sentence-transformers chromadb
    ```

### Step 4: Organize Data
1.  Inside your project folder, create a directory named `data`.
2.  **GitHub Repo:** Clone the repository you want to use as a knowledge source into the `data` folder.
    ```bash
    cd data
    git clone https://github.com/example/repo.git
    cd ..
    ```
3.  **Discord Export:** Place your Discord history export (e.g., `export.json` or a folder of CSVs) into the `data` folder.

### Step 5: Write the Ingestion Script (`ingest.py`)
Create a file named `ingest.py`. This script will load, chunk, embed, and store your data in the ChromaDB vector store.

*   *(The specific code for this will be developed in our next steps. It will involve using `LangChain` loaders to read the files, splitters to chunk them, and `ChromaDB` to save the embeddings.)*

---

## Phase 2: Building the Query Engine

### Step 6: Write the Query Script (`query.py`)
Create a file named `query.py`. This script will be used to ask questions.

*   *(This script will be developed after ingestion. It will initialize the connection to ChromaDB and Ollama, define a prompt template, and orchestrate the RAG chain to retrieve context and generate an answer.)*

### Step 7: Implement Retrieval and Generation
The `query.py` script will perform these actions:
1.  Take a user question as input.
2.  Connect to the existing ChromaDB database.
3.  Use the embedding model to find relevant documents.
4.  Connect to the local Ollama LLM (`http://localhost:11434`).
5.  Pass the question and the documents to the LLM.
6.  Print the response and the sources used.

### Step 8: Test the System
Once the `query.py` script is ready, you can run it from your terminal to ask questions and validate the quality of the responses.
```bash
python query.py "How do I fix the authentication bug?"
```

---

## Phase 3: Wrapping in an API (Future Enhancement)

### Step 9: Create a Web Server
To make the assistant more accessible, you can wrap the query logic in a simple web API using a framework like **FastAPI** or **Flask**.

### Step 10: Build a Simple UI
A basic HTML/JavaScript front-end could be built to provide a user-friendly chat interface that communicates with your API.
