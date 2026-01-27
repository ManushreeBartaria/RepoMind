import pickle
from RepoMind.retrieval.retrival import normalize_user_query, semantic_entry_discovery
from RepoMind.retrieval.feature1 import (
    extract_flow_subgraph,
    fetch_chunks_by_id,
    send_to_llm,
    flow_text,
)
from dotenv import load_dotenv
import subprocess

load_dotenv()


def run_feature1(user_query: str):
    refined_query = normalize_user_query(user_query, "explanation")

    with open("code_graph.pkl", "rb") as f:
        graph = pickle.load(f)

    if refined_query["needs_semantic_discovery"]:
        entry_nodes = semantic_entry_discovery(
            refined_query["concept_entities"],
            refined_query["queries"]["explanation"],
            graph,
        )
    else:
        entry_nodes = []

    if not entry_nodes:
        raise RuntimeError("No entry nodes found for Feature 1")

    flow_nodes = extract_flow_subgraph(graph, entry_nodes)

    if not flow_nodes:
        raise RuntimeError("No flow nodes extracted")

    docs = fetch_chunks_by_id(flow_nodes)

    if not docs:
        raise RuntimeError("No documents retrieved from vector DB")

    explanation = send_to_llm(
        docs,
        refined_query["queries"]["explanation"]
    )

    mermaid_text = flow_text(explanation)

    with open("flow.mmd", "w") as f:
        f.write(mermaid_text)

    subprocess.run(
        [
            r"C:\Program Files\nodejs\npx.cmd",
            "mmdc",
            "-i",
            "flow.mmd",
            "-o",
            "flow.svg"
        ],
        check=True
    )

    return explanation


if __name__ == "__main__":
    user_query = "Tell me how authentication works"
    result = run_feature1(user_query)
    print(result)
