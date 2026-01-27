import pickle
from typing import List, Dict
import networkx as nx
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import subprocess

def extract_impact_subgraph(graph, start_nodes, max_depth=4):
    impacted = set()
    paths = {}
    failure_points = []

    for start in start_nodes:
        if not graph.has_node(start):
            continue

        for succ in nx.descendants(graph, start):
            path = nx.shortest_path(graph, start, succ)
            impacted.add(succ)
            paths[succ] = path

            if len(path) > 1:
                failure_points.append({
                    "fails_at": succ,
                    "safe_until": path[-2],
                    "path": path
                })

    return {
        "start_nodes": start_nodes,
        "impacted_nodes": list(impacted),
        "paths": paths,
        "failure_points": failure_points
    }


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


def send_to_llm_impact(
    docs: List[Document],
    query: str,
    impact_data: Dict
) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a senior software architect performing CHANGE IMPACT ANALYSIS.

Context (code excerpts):
----------------
{context}
----------------

Impact Graph Analysis:
- Changed Node(s): {impact_data["start_nodes"]}
- Impacted Nodes: {impact_data["impacted_nodes"]}

Task:
1. Explain the FULL execution flow starting from the changed component.
2. Clearly state:
   - Which parts continue to work correctly
   - Where failures or incorrect behavior will begin (if any)
3. If the change is BREAKING:
   - Explain why it breaks
   - Explain how successor nodes are impacted
4. If the change is SAFE:
   - Explain why no downstream components fail
5. Provide RECOMMENDATIONS:
   - Safer alternatives
   - Refactoring or interface contracts if needed

Rules:
- Do NOT invent new code
- Do NOT repeat explanations unnecessarily
- Be precise and causal (X changes → Y breaks → Z fails)

Additional Requirement:
- Clearly state HOW LONG the system continues to work correctly.
- Identify:
  - Last Safe Component
  - First Failing Component
- Explain what triggers the failure at that point.


Now answer the following question:
{query}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content[0]["text"]


def impact_mermaid(impact_data, output_dir="artifacts"):
    os.makedirs(output_dir, exist_ok=True)

    mmd_path = os.path.join(output_dir, "feature2_impact.mmd")
    svg_path = os.path.join(output_dir, "feature2_impact.svg")

    lines = ["flowchart TD"]

    start = impact_data["start_nodes"][0]
    lines.append(f'{start}:::changed')

    for fp in impact_data["failure_points"]:
        safe = fp["safe_until"]
        fail = fp["fails_at"]
        lines.append(f"{safe} --> {fail}")

    lines.append("""
classDef changed fill:#FFD580,stroke:#333,stroke-width:2px;
classDef safe fill:#C8FACC,stroke:#333;
classDef fail fill:#FFB3B3,stroke:#333,stroke-width:2px;
""")

    for fp in impact_data["failure_points"]:
        lines.append(f"{fp['safe_until']}:::safe")
        lines.append(f"{fp['fails_at']}:::fail")

    mermaid_code = "\n".join(lines)

    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    subprocess.run(
        [
            r"C:\Program Files\nodejs\npx.cmd",
            "mmdc",
            "-i",
            mmd_path,
            "-o",
            svg_path
        ],
        check=True
    )

    return {
        "mmd_path": mmd_path,
        "svg_path": svg_path
    }

