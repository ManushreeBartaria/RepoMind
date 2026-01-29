import pickle

from RepoMind.retrieval.retrival import (
    normalize_user_query,
    semantic_entry_discovery
)

# -------- Feature 1 (Explanation) --------
from RepoMind.retrieval.feature1 import run_feature1

# -------- Feature 2 (Impact Analysis) --------
from RepoMind.retrieval.feature2 import run_feature2

# -------- Feature 3 (Visualization / Structure) --------
from RepoMind.retrieval.feature3 import run_feature3


# =========================================================
# Feature 1 Router
# =========================================================
def run_explanation_feature(refined, graph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["explanation"],
        graph
    )

    # Feature 1 returns (explanation, svg_path)
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

    return {
        "text": explanation,
        "structure": structure
    }


# =========================================================
# Feature 2 Router
# =========================================================
def run_impact_feature(refined, graph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["impact_analysis"],
        graph
    )[:1]
    impact_result = run_feature2(
        graph=graph,
        changed_nodes=entry_nodes,
        query=refined["queries"]["impact_analysis"]
    )

    structure = run_feature3(
        graph=graph,
        nodes=impact_result[2],
        output_dir="artifacts",
        filename="feature2_structure"
    )

    return {
        "text": impact_result[0],
        "impact_data": impact_result[1],
        "structure": structure
    }


# =========================================================
# Feature 3 Router (Standalone)
# =========================================================
def run_structure_feature(refined, graph):
    entry_nodes = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["call_flow"],
        graph
    )

    return run_feature3(
        graph=graph,
        nodes=entry_nodes,
        output_dir="artifacts",
        filename="feature3_structure"
    )


# =========================================================
# Main Router
# =========================================================
def run(user_query: str, frontend_section: str):
    refined = normalize_user_query(user_query, frontend_section)

    with open("code_graph.pkl", "rb") as f:
        graph = pickle.load(f)

    responses = {}
    primary = refined["primary_intent"]

    if primary == "explanation":
        responses["explanation"] = run_explanation_feature(refined, graph)

    elif primary == "impact_analysis":
        responses["impact_analysis"] = run_impact_feature(refined, graph)

    elif primary == "call_flow":
        responses["system_structure"] = run_structure_feature(refined, graph)

    return {
        "intent": refined["primary_intent"],
        "confidence": refined["confidence"],
        "responses": responses
    }


# =========================================================
# Local Test
# =========================================================
if __name__ == "__main__":
    # q1 = "Explain how authentication works end to end"
    # print(run(q1, "explanation"))

    # q2 = "If I change login API what breaks"
    # print(run(q2, "impact_analysis"))

    q3 = "Show system structure of authentication"
    print(run(q3, "call_flow"))
