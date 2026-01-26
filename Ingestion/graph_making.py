import networkx as nx
import matplotlib.pyplot as plt
import pickle
def create_graph(all_chunks, all_relations):
    G = nx.DiGraph()
    def chunk_id(chunk):
        return f"{chunk['file_path']}::{chunk['name']}"
    name_to_node = {}
    for chunk in all_chunks:
        cid = chunk_id(chunk)
        name_to_node.setdefault(chunk["name"], []).append(cid)

    def resolve_node(name):
        nodes = name_to_node.get(name)
        return nodes[0] if nodes else None

    for chunk in all_chunks:
        node_id = chunk_id(chunk)
        G.add_node(
            node_id,
            type=chunk["type"],
            file=str(chunk["file_path"]),
            language=chunk.get("language", "unknown"),
        )

    for rel in all_relations:
        src = resolve_node(rel["from"])
        dst = resolve_node(rel["to"])
        if not src or not dst:
            continue
        G.add_edge(
            src,
            dst,
            type=rel["type"],
            language=rel["language"],
            confidence=rel.get("confidence", "unknown"),
        )
        
    with open("code_graph.pkl", "wb") as f:
        pickle.dump(G, f)

    return G
