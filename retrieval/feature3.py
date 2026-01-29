import os
import subprocess
from typing import List, Dict
import networkx as nx


# =========================================================
# Feature 3 — Structure Graph Builder (NO LLM)
# =========================================================

def run_feature3(
    graph: nx.DiGraph,
    nodes: List[str],
    output_dir: str = "artifacts",
    filename: str = "feature_structure"
) -> Dict:
    """
    Generates a STRUCTURAL GRAPH (Mermaid + SVG) for the given nodes.

    - Uses ONLY graph topology
    - NO LLM calls
    - NO caching
    - Graph reflects the SAME nodes used in explanation / impact
    """

    if not nodes:
        return {}

    os.makedirs(output_dir, exist_ok=True)

    mmd_path = os.path.join(output_dir, f"{filename}.mmd")
    svg_path = os.path.join(output_dir, f"{filename}.svg")

    lines = ["flowchart TD"]
    node_ids = {}

    def safe(node_id: str) -> str:
        return node_id.replace("\\", "_").replace("/", "_").replace("::", "_")

    # -------------------------------------------------
    # Node rendering
    # -------------------------------------------------
    for node in nodes:
        if not graph.has_node(node):
            continue

        data = graph.nodes[node]

        func = node.split("::")[-1]
        file = data.get("file", "unknown")
        params = data.get("params", [])
        ntype = data.get("type", "unknown")

        params_str = ", ".join(params) if params else "—"
        nid = safe(node)
        node_ids[node] = nid

        label = (
            f"<b>{func}</b><br/>"
            f"<small>({params_str})</small><br/>"
            f"<small>{file}</small><br/>"
            f"<small>[{ntype}]</small>"
        )

        lines.append(f'{nid}["{label}"]')

    # -------------------------------------------------
    # Edge rendering (ONLY between included nodes)
    # -------------------------------------------------
    for src in nodes:
        for dst in graph.successors(src):
            if src in node_ids and dst in node_ids:
                lines.append(f"{node_ids[src]} --> {node_ids[dst]}")

    # -------------------------------------------------
    # Write Mermaid
    # -------------------------------------------------
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # -------------------------------------------------
    # Render SVG
    # -------------------------------------------------
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
        "svg_path": svg_path,
        "total_nodes": len(node_ids)
    }
