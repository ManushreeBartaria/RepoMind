import os
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
 
from dotenv import load_dotenv
load_dotenv()

def user_query(query: str, vector_store_path: str = "db/chroma_db")-> List[Document]:
    """Process a user query against a Chroma vector store.

    Args:
        query (str): The user's query.
        vector_store_path (str): Path to the Chroma vector store.

    Returns:
        List[Document]: Retrieved documents relevant to the query.
    """
    # Initialize the embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Load the Chroma vector store
    vector_store = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_model
    )

    # Perform similarity search
    results: List[Document] = vector_store.similarity_search(query, k=5)

    return results


if __name__ == "__main__":
    sample_query = "Tell me about routes"
    retrieved_docs = user_query(sample_query)
    for i, doc in enumerate(retrieved_docs):
        print(f"Document {i+1}:\n{doc.page_content}\n")
