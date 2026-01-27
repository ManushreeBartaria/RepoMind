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



import json

def normalize_user_query(
    user_query: str,
    frontend_section: str
) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
    system_prompt = f"""
You are an intent normalization engine for a code intelligence system.

Your task:
- DO NOT answer the user question.
- DO NOT add new meaning.
- DO NOT remove meaning.
- DO NOT assume context not present in the query.
- ONLY classify intent(s) and rewrite the SAME question
  in intent-specific technical language.

Primary intent is given by the frontend section.
You may infer secondary intents if clearly implied.

Allowed intents:
- explanation
- impact_analysis
- call_flow

Frontend-selected primary intent: {frontend_section}

Return ONLY valid JSON in the following format:

{{
  "primary_intent": "<one of allowed intents>",
  "secondary_intents": ["<optional intents>"],
  "queries": {{
    "<intent>": "<reformulated query preserving meaning>"
  }},
  "entities": ["<symbols, functions, classes if mentioned>"],
  "confidence": <float between 0 and 1>
}}
"""

    user_prompt = f"""
User query:
"{user_query}"
"""

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        # Safe fallback — never crash the system
        parsed = {
            "primary_intent": frontend_section,
            "secondary_intents": [],
            "queries": {
                frontend_section: user_query
            },
            "entities": [],
            "confidence": 0.5
        }

    return parsed



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
        