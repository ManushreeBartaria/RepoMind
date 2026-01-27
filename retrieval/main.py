import pickle
from RepoMind.retrieval.retrival import (
    normalize_user_query,
    semantic_entry_discovery
)

from RepoMind.retrieval.feature1 import (
    extract_flow_subgraph,
    fetch_chunks_by_id,
    send_to_llm as run_explanation
)

from RepoMind.retrieval.feature2 import (
    extract_impact_subgraph,
    fetch_chunks_by_id as fetch_chunks_impact,
    send_to_llm_impact,
    impact_mermaid
)


def run_explanation_feature(refined_query, graph):
    entry_nodes = semantic_entry_discovery(
        refined_query["concept_entities"],
        refined_query["queries"]["explanation"],
        graph
    )

    flow_nodes = extract_flow_subgraph(graph, entry_nodes)
    docs = fetch_chunks_by_id(flow_nodes)

    return run_explanation(
        docs,
        refined_query["queries"]["explanation"]
    )


def run_impact_feature(refined_query, graph):
    entry_nodes = semantic_entry_discovery(
        refined_query["concept_entities"],
        refined_query["queries"]["impact_analysis"],
        graph
    )

    impact_data = extract_impact_subgraph(graph, entry_nodes)

    all_nodes = (
        impact_data["start_nodes"] +
        impact_data["impacted_nodes"]
    )

    docs = fetch_chunks_impact(all_nodes)

    text_result = send_to_llm_impact(
        docs,
        refined_query["queries"]["impact_analysis"],
        impact_data
    )

    diagram_files = impact_mermaid(impact_data)

    last_safe = None
    first_failure = None
    if impact_data["failure_points"]:
        last_safe = impact_data["failure_points"][0]["safe_until"]
        first_failure = impact_data["failure_points"][0]["fails_at"]

    return {
        "text": text_result,
        "last_safe_point": last_safe,
        "first_failure_point": first_failure,
        "impact_diagram": diagram_files["svg_path"]
    }


def run(user_query: str, frontend_section: str):
    refined_query = normalize_user_query(user_query, frontend_section)

    with open("code_graph.pkl", "rb") as f:
        graph = pickle.load(f)

    responses = {}
    primary_intent = refined_query["primary_intent"]

    if primary_intent == "explanation":
        responses["explanation"] = run_explanation_feature(
            refined_query, graph
        )

    elif primary_intent == "impact_analysis":
        responses["impact_analysis"] = run_impact_feature(
            refined_query, graph
        )

    secondary_intents = refined_query.get("secondary_intents", [])
    for intent in secondary_intents:
        if intent == "call_flow":
            responses["call_flow"] = run_explanation_feature(
                refined_query, graph
            )

    return {
        "intent": refined_query["primary_intent"],
        "confidence": refined_query["confidence"],
        "responses": responses
    }


if __name__ == "__main__":
    user_query = "If I change login_user logic, what will break?"
    result = run(user_query, "impact_analysis")
    print(result)
