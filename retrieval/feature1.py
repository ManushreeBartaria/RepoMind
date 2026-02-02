import os
import pickle
import subprocess
from typing import List
from dotenv import load_dotenv
import networkx as nx
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
load_dotenv()


def extract_flow_subgraph(graph, entry_nodes, max_depth=2):
    visited = set()
    ordered_nodes = []
    def dfs(node, depth):
        if depth > max_depth or node in visited:
            return
        visited.add(node)
        ordered_nodes.append(node)
        for succ in graph.successors(node):
            dfs(succ, depth + 1)
    for entry in entry_nodes:
        dfs(entry, 0)
    return ordered_nodes


def fetch_chunks_by_id(chunk_ids: List[str]) -> List[Document]:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="RepoMind/db/chroma_db",
        embedding_function=embedding_model
    )

    results = vectorstore.get(
        where={"chunk_id": {"$in": chunk_ids}}
    )

    docs = []
    for content, metadata in zip(results["documents"], results["metadatas"]):
        docs.append(Document(page_content=content, metadata=metadata))

    return docs



def send_to_llm(docs: List[Document], query: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
    You are an expert full-stack software architect and educator.
    Using ONLY the information provided in the context below, explain the COMPLETE
    end-to-end execution flow of the system — from frontend to backend.
    Context:
    ----------------
    {context}
    ----------------
    Task:
    Explain the full flow starting from the frontend user action all the way
    to the backend response and back to the UI.

    Now answer the following question:
    {query}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content[0]["text"]


def flow_text(result: str) -> str:
    prompt = f'''
    You are a senior system architect.
    Convert the following system explanation into a Mermaid FLOWCHART.
    Rules:
    - Output ONLY valid Mermaid flowchart syntax
    - Use flowchart TD
    - Use arrows (-->)
    - Include function names
    - Include API endpoints
    - Do NOT add explanations
    - Do NOT add markdown backticks

    Explanation:
    ----------------
    {result}
    ----------------
    '''
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content[0]["text"]

def normalize_mermaid(text: str) -> str:
    lines = text.splitlines()
    edges = []
    node_map = {}
    node_counter = 1

    def get_node(label):
        nonlocal node_counter
        label = label.strip()
        if label not in node_map:
            node_id = f"N{node_counter}"
            node_counter += 1
            node_map[label] = node_id
        return node_map[label]

    for line in lines:
        if "-->" not in line:
            continue
        parts = line.split("-->")
        if len(parts) != 2:
            continue
        left = parts[0].strip()
        right = parts[1].strip()

        src = get_node(left)
        dst = get_node(right)
        edges.append((src, dst))

    output = ["flowchart TD"]

    for label, node_id in node_map.items():
        safe_label = label.replace('"', "'")
        output.append(f'{node_id}["{safe_label}"]')

    for src, dst in edges:
        output.append(f"{src} --> {dst}")

    return "\n".join(output)


if __name__ == "__main__":
    with open("code_graph.pkl", "rb") as f:
        graph = pickle.load(f)
    flow_nodes = extract_flow_subgraph(graph, entry_nodes)
    docs = fetch_chunks_by_id(flow_nodes)
    explanation = send_to_llm(docs, explanation_query)
    raw_flow = flow_text(explanation)
    mermaid_flow = normalize_mermaid(raw_flow)
    print(explanation)
    with open("flow.mmd", "w") as f:
        f.write(mermaid_flow)
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
