import os
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import subprocess
from RepoMind.retrieval.feature1 import send_to_llm, flow_text
load_dotenv()
def user_query(query: str, vector_store_path: str = "db/chroma_db")-> List[Document]:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_model
    )
    results: List[Document] = vector_store.similarity_search(query, k=5)
    return results

def reformulate_query_and_detect_intent(query: str) -> Dict[str, str]:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0
    )
    prompt = ChatPromptTemplate.from_template(
"""You are an expert query understanding and rewriting engine for a Retrieval-Augmented Generation (RAG) system focused on software architecture.

Your task:
1. Identify the PRIMARY intent of the user query.
2. ALWAYS rewrite the query into a more explicit, system-level, and search-optimized form.
3. Preserve the original meaning, but EXPAND vague queries into concrete technical requests.

Intent classification rules:
- Any query asking HOW a backend works, processes requests, handles logic, or manages data
  → backend_execution_flow
- Queries about UI behavior, frontend components, state, or rendering
  → frontend_execution_flow
- Queries asking about the complete system from frontend to backend
  → fullstack_architecture_flow
- Queries about APIs, endpoints, routes, HTTP methods, or payloads
  → api_explanation
- Queries about specific code, functions, classes, or errors
  → code_explanation
- Anything else
  → general_question

Rewriting rules (MANDATORY):
- Convert generic questions into detailed, technical, system-level queries.
- Include backend concepts such as controllers, services, database, request/response lifecycle when relevant.
- The reformulated query MUST be different from the original query.

User Query:
"{query}"

Return ONLY valid JSON in EXACTLY this format:
{
  "intent": "<intent>",
  "reformulated_query": "<rewritten, explicit, technical query>"
}
"""
    )

    chain = prompt | llm

    try:
        raw = chain.invoke({"query": query})
        text = extract_text(raw.content)

        import json
        data = json.loads(text)

        return {
            "intent": data["intent"].strip().lower(),
            "reformulated_query": data["reformulated_query"].strip()
        }

    except Exception as e:
        print("INTENT PARSING FAILED:", e)
        print("RAW MODEL OUTPUT:", text if 'text' in locals() else None)

        return {
            "intent": "general_question",
            "reformulated_query": query
        }

def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(c) for c in content)
    return str(content)


if __name__ == "__main__":
    sample_query = "Tell me how backend works"
    meta = reformulate_query_and_detect_intent(sample_query)
    intent = meta["intent"]
    refined_query = meta["reformulated_query"]
    print("Intent:", intent)
    print("Rewritten Query:", refined_query)
    retrieved_docs = user_query(refined_query)
    result = send_to_llm(retrieved_docs, refined_query)
    flow_output=flow_text(result)
    with open("flow.mmd", "w") as f:
        f.write(flow_output)
    md_file=os.path.abspath("flow.mmd")
    png_file=os.path.abspath("flow.png")    
    subprocess.run([
        r"C:\Program Files\nodejs\npx.cmd", "mmdc", "-i", md_file, "-o", png_file
    ], check=True)
        