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

from RepoMind.retrieval.feature3 import (
    extract_call_chain,
    fetch_chunks_by_id as fetch_chunks_call,
    send_to_llm_call_flow,
    call_flow_mermaid
)


def run_explanation_feature(refined, graph):
    entry = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["explanation"],
        graph
    )
    nodes = extract_flow_subgraph(graph, entry)
    docs = fetch_chunks_by_id(nodes)
    return run_explanation(docs, refined["queries"]["explanation"])


def run_impact_feature(refined, graph):
    entry = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["impact_analysis"],
        graph
    )

    impact = extract_impact_subgraph(graph, entry)
    docs = fetch_chunks_impact(
        impact["start_nodes"] + impact["impacted_nodes"]
    )

    text = send_to_llm_impact(
        docs,
        refined["queries"]["impact_analysis"],
        impact
    )

    diagram = impact_mermaid(impact)

    last_safe = None
    first_fail = None
    if impact["failure_points"]:
        last_safe = impact["failure_points"][0]["safe_until"]
        first_fail = impact["failure_points"][0]["fails_at"]

    return {
        "text": text,
        "last_safe_point": last_safe,
        "first_failure_point": first_fail,
        "impact_diagram": diagram
    }


def run_call_flow_feature(refined, graph):
    entry = semantic_entry_discovery(
        refined["concept_entities"],
        refined["queries"]["call_flow"],
        graph
    )

    call_chain = extract_call_chain(graph, entry)
    docs = fetch_chunks_call(call_chain)

    text = send_to_llm_call_flow(
        docs,
        refined["queries"]["call_flow"]
    )

    diagram = call_flow_mermaid(call_chain)

    return {
        "call_sequence": text,
        "call_flow_diagram": diagram
    }


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
        responses["call_flow"] = run_call_flow_feature(refined, graph)

    for intent in refined.get("secondary_intents", []):
        if intent == "call_flow" and "call_flow" not in responses:
            responses["call_flow"] = run_call_flow_feature(refined, graph)

    return {
        "intent": refined["primary_intent"],
        "confidence": refined["confidence"],
        "responses": responses
    }


if __name__ == "__main__":
    query = "Show me the call flow for authentication"
    result = run(query, "call_flow")
    print(result)
