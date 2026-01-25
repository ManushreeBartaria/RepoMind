import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
load_dotenv()

def user_query(query: str, vector_store_path: str = "db/chroma_db")-> List[Document]:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_model
    )
    results: List[Document] = vector_store.similarity_search(query, k=5)
    return results

def send_to_llm(docs: List[Document], query: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
            You are an expert full-stack software architect and educator.

            Using ONLY the information provided in the context below, explain the COMPLETE
            end-to-end execution flow of the system — from frontend to backend.

            Your explanation must help a beginner clearly understand how data moves
            through the system.

            Context:
            ----------------
            {context}
            ----------------

            Task:
            Explain the full flow starting from the frontend user action all the way
            to the backend response and back to the UI.

            Instructions:
            1. Start from the USER ACTION (e.g., button click, form submission).
            2. Clearly mention:
            - Which frontend function is triggered
            - What inputs it receives (use MOCK VALUES)
            3. Explain:
            - API call details (endpoint, method, payload)
            - Which backend controller/function receives it
            4. For each backend step:
            - Function name
            - Input parameters (with example values)
            - Internal processing logic (brief but clear)
            - What the function returns
            5. Trace the response:
            - How it travels back through the backend
            - How the frontend receives and handles it
            6. End with:
            - Final UI update or output shown to the user

            Output Requirements:
            - Present the flow in a STEP-BY-STEP numbered format
            - Include MOCK DATA (example JSON, variables, return values)
            - Use SIMPLE language, but be technically correct
            - Clearly show direction of data flow (→ arrows where helpful)
            - Do NOT invent new functions or APIs not present in the context

            Goal:
            By the end, the reader should be able to mentally visualize
            the entire system flow without seeing the code.

            Now answer the following question:
            {query}
            """
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content[0]["text"]


if __name__ == "__main__":
    sample_query = "Tell me about routes"
    retrieved_docs = user_query(sample_query)
    result = send_to_llm(retrieved_docs, sample_query)
    print(result)
        