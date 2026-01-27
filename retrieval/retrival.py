import json
import pickle
from typing import List
from dotenv import load_dotenv

import networkx as nx
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def semantic_entry_discovery(
    concept_entities: List[str],
    explanation_query: str,
    graph
) -> List[str]:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
        persist_directory="RepoMind/db/chroma_db",
        embedding_function=embedding_model
    )

    candidate_docs: List[Document] = vectorstore.similarity_search(
        explanation_query,
        k=10
    )

    candidate_nodes = []
    for doc in candidate_docs:
        chunk_id = doc.metadata.get("chunk_id")
        if chunk_id and graph.has_node(chunk_id):
            candidate_nodes.append(chunk_id)

    scored_nodes = []
    for node in candidate_nodes:
        out_degree = graph.out_degree(node)
        in_degree = graph.in_degree(node)
        reachable = len(nx.descendants(graph, node))
        score = (out_degree * 2) + reachable - in_degree
        scored_nodes.append((node, score))

    if not scored_nodes:
        return []

    scored_nodes.sort(key=lambda x: x[1], reverse=True)
    return [scored_nodes[0][0]]


def normalize_user_query(user_query: str, frontend_section: str) -> dict:
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

    Entity extraction rules:
    - If the query mentions a specific function, class, or symbol, list it under "symbol_entities".
    - If the query refers to a high-level concept, list it under "concept_entities".
    - Do NOT invent entities.

    Return ONLY valid JSON in the following format:
    {{
      "primary_intent": "...",
      "secondary_intents": [],
      "queries": {{}},
      "symbol_entities": [],
      "concept_entities": [],
      "needs_semantic_discovery": true,
      "confidence": 0.0
    }}
    """

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
    )

    try:
        return json.loads(response.content[0]["text"])
    except Exception:
        return {
            "primary_intent": frontend_section,
            "secondary_intents": [],
            "queries": {frontend_section: user_query},
            "symbol_entities": [],
            "concept_entities": [],
            "needs_semantic_discovery": False,
            "confidence": 0.5,
        }
