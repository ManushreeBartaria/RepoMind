from typing import Dict, Any
import networkx as nx
from pathlib import Path

from .retrival import (
    normalize_user_query,
    semantic_entry_discovery
)

# -------- Feature 1 (Explanation) --------
from .feature1 import run_feature1

# -------- Feature 2 (Impact Analysis) --------
from .feature2 import run_feature2

# -------- Feature 3 (Visualization / Structure) --------
from .feature3 import run_feature3


# =========================================================
# Feature 1 Router
# =========================================================
def run_explanation_feature(refined: Dict, graph: nx.DiGraph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["explanation"],
        graph
    )

    explanation, flow_nodes = run_feature1(
        graph=graph,
        entry_nodes=entry_nodes,
        query=refined["queries"]["explanation"]
    )

    structure = run_feature3(
        graph=graph,
        nodes=flow_nodes,
        output_dir="artifacts",
        filename="feature1_structure"
    )

    svg_path = structure.get("svg_path")
    image_url = f"/artifacts/{Path(svg_path).name}"

    return {
        "text": explanation,
        "structure": structure,
        "image_url": image_url
    }


# =========================================================
# Feature 2 Router
# =========================================================
def run_impact_feature(refined: Dict, graph: nx.DiGraph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["impact_analysis"],
        graph
    )[:1]

    explanation, impact_data, involved_nodes = run_feature2(
        graph=graph,
        changed_nodes=entry_nodes,
        query=refined["queries"]["impact_analysis"]
    )

    structure = run_feature3(
        graph=graph,
        nodes=involved_nodes,
        output_dir="artifacts",
        filename="feature2_structure"
    )

    svg_path = structure.get("svg_path")
    image_url = f"/artifacts/{Path(svg_path).name}"

    return {
        "text": explanation,
        "impact_data": impact_data,
        "structure": structure,
        "image_url": image_url
    }


# =========================================================
# Feature 3 Router (Standalone)
# =========================================================
def run_structure_feature(refined: Dict, graph: nx.DiGraph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["call_flow"],
        graph
    )

    structure = run_feature3(
        graph=graph,
        nodes=entry_nodes,
        output_dir="artifacts",
        filename="feature3_structure"
    )

    svg_path = structure.get("svg_path")
    image_url = f"/artifacts/{Path(svg_path).name}"


    return {
        "structure": structure,
        "image_url": image_url
    }


# =========================================================
# 🚀 MAIN RETRIEVAL ENTRYPOINT (BACKEND CALLS THIS)
# =========================================================
def run(
    user_query: str,
    frontend_section: str,
    graph: nx.DiGraph
) -> Dict[str, Any]:
    """
    PURE RETRIEVAL ORCHESTRATOR.

    Responsibilities:
    - Normalize user intent
    - Discover semantic entry points
    - Route to correct feature
    - Aggregate responses

    Does NOT:
    - Load graph
    - Load vector DB
    - Manage lifecycle
    """

    refined = normalize_user_query(
        user_query,
        frontend_section
    )

    responses = {}
    primary = refined["primary_intent"]

    if primary == "explanation":
        responses["explanation"] = run_explanation_feature(
            refined,
            graph
        )

    elif primary == "impact_analysis":
        responses["impact_analysis"] = run_impact_feature(
            refined,
            graph
        )

    elif primary == "call_flow":
        responses["system_structure"] = run_structure_feature(
            refined,
            graph
        )

    return {
        "intent": refined["primary_intent"],
        "confidence": refined.get("confidence", 0.0),
        "responses": responses
    }


# =========================================================
# Optional local testing (dev-only)
# =========================================================
if __name__ == "__main__":
    import pickle

    with open("code_graph.pkl", "rb") as f:
        graph = pickle.load(f)

    q = "Show system structure of authentication"
    print(
        run(
            user_query=q,
            frontend_section="call_flow",
            graph=graph
        )
    )