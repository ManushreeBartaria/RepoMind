from typing import List, Dict, Tuple
from collections import deque
import networkx as nx

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# =========================================================
# Impact traversal (BFS with causal tracking)
# =========================================================
def extract_impact_subgraph(
    graph: nx.DiGraph,
    start_nodes: List[str],
    max_depth: int = 4
) -> Dict:
    """
    BFS-based causal impact traversal.
    Identifies:
    - impacted nodes
    - execution chains
    - first failure points
    """

    impacted_nodes = set()
    execution_chains = []
    failure_points = []

    for start in start_nodes:
        if not graph.has_node(start):
            continue

        visited = set()
        queue = deque([(start, 0, [start])])

        level_map = {}
        first_failure = None
        failure_path = []
        last_safe = start

        while queue:
            node, level, path = queue.popleft()

            if node in visited or level > max_depth:
                continue

            visited.add(node)
            impacted_nodes.add(node)
            level_map[node] = level

            successors = list(graph.successors(node))

            # Failure heuristic:
            # leaf node that is not a utility/helper
            if (
                node != start
                and not successors
                and graph.nodes[node].get("type") not in {"utility", "helper"}
                and first_failure is None
            ):
                first_failure = node
                failure_path = path
                last_safe = path[-2] if len(path) > 1 else start
                break

            for succ in successors:
                queue.append((succ, level + 1, path + [succ]))

        if first_failure:
            failure_points.append({
                "entry": start,
                "safe_until": last_safe,
                "fails_at": first_failure,
                "path": failure_path,
                "working_depth": level_map.get(last_safe, 0)
            })

        execution_chains.append({
            "entry": start,
            "working_nodes": [
                n for n, lvl in level_map.items()
                if first_failure is None or lvl < level_map.get(first_failure, float("inf"))
            ],
            "first_failure": first_failure,
            "failure_path": failure_path,
            "levels": level_map
        })

    return {
        "start_nodes": start_nodes,
        "impacted_nodes": sorted(impacted_nodes),
        "failure_points": failure_points,
        "execution_chains": execution_chains
    }


# =========================================================
# Chunk retrieval
# =========================================================
def fetch_chunks_by_id(
    chunk_ids: List[str]
) -> List[Document]:
    if not chunk_ids:
        return []

    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory="RepoMind/db/chroma_db",
        embedding_function=embedding_model
    )

    results = vectorstore.get(
        where={"chunk_id": {"$in": chunk_ids}}
    )

    docs = []
    for content, metadata in zip(
        results.get("documents", []),
        results.get("metadatas", [])
    ):
        docs.append(
            Document(
                page_content=content,
                metadata=metadata
            )
        )

    return docs


# =========================================================
# Impact explanation LLM
# =========================================================
def send_to_llm_impact(
    docs: List[Document],
    query: str,
    impact_data: Dict
) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0
    )

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    execution_summary = ""
    for chain in impact_data["execution_chains"]:
        execution_summary += f"""
Entry Point: {chain['entry']}
Working Components:
{' → '.join(chain['working_nodes'])}

First Failure: {chain['first_failure']}
"""

    prompt = f"""
You are a senior software architect performing CHANGE IMPACT ANALYSIS.

Context:
----------------
{context}
----------------

Execution Summary:
{execution_summary}

Failure Points:
{impact_data['failure_points']}

Tasks:
1. Trace execution from entry point
2. Identify last safe component
3. Identify first failing component
4. Explain WHY failure happens
5. Describe downstream impact
6. Provide mitigation suggestions

Question:
{query}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content[0]["text"]


# =========================================================
# Public API
# =========================================================
def run_feature2(
    graph: nx.DiGraph,
    changed_nodes: List[str],
    query: str
) -> Tuple[str, Dict, List[str]]:
    """
    Returns:
    - impact explanation text
    - raw impact data
    - ALL nodes involved (for Feature 3 graph rendering)
    """

    impact_data = extract_impact_subgraph(
        graph,
        changed_nodes
    )

    involved_nodes = list(
        set(
            impact_data["start_nodes"]
            + impact_data["impacted_nodes"]
        )
    )

    docs = fetch_chunks_by_id(
        involved_nodes
    )

    explanation = send_to_llm_impact(
        docs,
        query,
        impact_data
    )

    return explanation, impact_data, involved_nodes
