import os
import subprocess
import networkx as nx
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def extract_call_chain(graph: nx.DiGraph, entry_nodes: List[str], max_depth=4) -> List[str]:
    visited = set()
    ordered = []

    def dfs(node, depth):
        if node in visited or depth > max_depth:
            return
        visited.add(node)
        ordered.append(node)
        for succ in graph.successors(node):
            dfs(succ, depth + 1)

    for entry in entry_nodes:
        dfs(entry, 0)

    return ordered


def fetch_chunks_by_id(chunk_ids: List[str]) -> List[Document]:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="RepoMind/db/chroma_db",
        embedding_function=embedding_model
    )

    if not chunk_ids:
        return []

    results = vectorstore.get(
        where={"chunk_id": {"$in": chunk_ids}}
    )

    docs = []
    for content, metadata in zip(results["documents"], results["metadatas"]):
        docs.append(Document(page_content=content, metadata=metadata))

    return docs


def send_to_llm_call_flow(docs: List[Document], query: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a software execution tracing engine.

Using ONLY the context below, list the EXACT call sequence
that occurs during execution.

Rules:
- Output a numbered list
- Each step must be a function or method name
- Follow actual execution order
- Do NOT explain WHY
- Do NOT summarize
- Do NOT invent calls

Context:
----------------
{context}
----------------

Now answer the following question:
{query}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content[0]["text"]


def call_flow_mermaid(call_chain: List[str], output_dir="artifacts"):
    os.makedirs(output_dir, exist_ok=True)

    mmd_path = os.path.join(output_dir, "feature3_call_flow.mmd")
    svg_path = os.path.join(output_dir, "feature3_call_flow.svg")

    lines = ["flowchart TD"]

    for i in range(len(call_chain) - 1):
        lines.append(f'{call_chain[i]} --> {call_chain[i+1]}')

    mermaid_code = "\n".join(lines)

    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    subprocess.run(
        [
            r"C:\\Program Files\\nodejs\\npx.cmd",
            "mmdc",
            "-i",
            mmd_path,
            "-o",
            svg_path
        ],
        check=True
    )

    return svg_path
