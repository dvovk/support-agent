import argparse
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM as Ollama # Updated import and aliasing for consistency
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import CrossEncoder # Using a cross-encoder for re-ranking
import logging
import os

# --- Configuration ---
PERSIST_DIRECTORY = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(question: str):
    """
    Main function to ask a question to the support assistant using prioritized retrieval.
    """
    logger.info("Loading knowledge bases from ChromaDB...")
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Load the two existing vector stores
    github_vectorstore = Chroma(persist_directory="chroma_db_github", embedding_function=embeddings)
    discord_vectorstore = Chroma(persist_directory="chroma_db_discord", embedding_function=embeddings)

    # Initialize the Ollama LLM
    logger.info(f"Initializing Ollama with model: {OLLAMA_MODEL}")
    llm = Ollama(model=OLLAMA_MODEL)

    # Create two retrievers with different search settings
    github_retriever = github_vectorstore.as_retriever(search_kwargs={"k": 6})
    discord_retriever = discord_vectorstore.as_retriever(search_kwargs={"k": 6})

    # --- Retrieve from both sources ---
    logger.info("Retrieving relevant documents from GitHub and Discord...")
    github_docs = github_retriever.invoke(question)
    discord_docs = discord_retriever.invoke(question)
    
    # Combine and de-duplicate if necessary (simple combination for now)
    retrieved_docs = github_docs + discord_docs

    # --- Re-ranking with a cross-encoder ---
    logger.info("Initializing cross-encoder for re-ranking...")
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Create pairs of [question, document_content] for the cross-encoder
    pairs = [[question, doc.page_content] for doc in retrieved_docs]
    
    # Predict the scores
    scores = cross_encoder.predict(pairs)
    
    # Combine docs with their scores and sort
    scored_docs = sorted(zip(scores, retrieved_docs), key=lambda x: x[0], reverse=True)
    
    # Keep the top N documents (e.g., top 4)
    top_n = 4
    retrieved_docs = [doc for score, doc in scored_docs[:top_n]]
    logger.info(f"Re-ranked documents (top {top_n}): {len(retrieved_docs)}")
    
    # --- Debugging Output ---
    print("\n" + "="*50)
    print("Retrieved Context (for debugging):")
    print("="*50)
    for i, doc in enumerate(retrieved_docs):
        print(f"--- Document {i+1} --")
        print(f"Source: {doc.metadata.get('source', 'N/A')}")
        print(f"Content: {doc.page_content[:500]}...")
        print("-"*(len(str(i+1))+14))
    print("="*50 + "\n")

    # --- RAG Chain ---
    template = """
You are a senior support engineer for Erigon. Your task is to answer the user's question based on the provided context.

1.  **Analyze the User's Problem:** Understand the user's issue from the "Question" section.
2.  **Find the Solution:** Search the "Context" for a direct solution, especially for any commands to run.
3.  **Provide the Answer:**
    *   If you find a solution, provide a clear, step-by-step answer.
    *   If the solution involves a command, present the command clearly.
    *   If you don't find a direct solution, state that and ask for more information.
4.  **Cite Your Sources:** Always mention the source of your information.

Context:
{context}

Question:
{question}

Answer:
"""
    prompt = PromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join([f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}" for doc in docs])

    rag_chain = (
        {"context": lambda x: format_docs(retrieved_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info("Invoking the RAG chain to find an answer...")
    answer = rag_chain.invoke(question)

    print("\n" + "="*50)
    print("Question:", question)
    print("="*50)
    print("Answer:")
    print(answer)
    print("="*50 + "\n")
    log_query_and_answer(question, answer)

def log_query_and_answer(question, answer):
    """
    Logs the question and answer to a file.
    """
    with open("queries_and_answers.log", "a") as f:
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n")
        f.write("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the RAG support assistant.")
    parser.add_argument("question", type=str, help="The question you want to ask.")
    args = parser.parse_args()
    
    main(args.question)
