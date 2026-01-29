from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from pathlib import Path
from typing import List
import json

load_dotenv()
JS_LANGUAGE = Language(tsjs.language())
def js_ast_parser(file_path: Path):
    chunks = []
    seen_nodes = set()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()
    parser = Parser(JS_LANGUAGE)
    tree = parser.parse(source.encode("utf-8"))
    def extract_identifier(node):
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None
    def get_chunk_type(node):
        if node.type == "function_declaration":
            return "function"
        if node.type == "class_declaration":
            return "class"
        if node.type == "method_definition":
            if node.parent and node.parent.type == "class_body":
                for child in node.children:
                    if child.type == "static":
                        return "static_method"
                return "method"
        if node.type == "arrow_function":
            if node.parent and node.parent.type == "variable_declarator":
                return "arrow_function"

        return None
    def walk(node):
        if id(node) in seen_nodes:
            return
        seen_nodes.add(id(node))
        chunk_type = get_chunk_type(node)
        if chunk_type:
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            name = extract_identifier(node)
            if not name and node.parent:
                name = extract_identifier(node.parent)
            chunks.append({
                "name": name or file_path.stem,
                "file_path": file_path,
                "type": chunk_type,
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
                "decorators": [],  # JavaScript typically uses decorators via @ syntax in TypeScript
            })
        for child in node.children:
            walk(child)
    walk(tree.root_node)
    if not chunks:
        chunks.append({
            "name": file_path.stem,
            "file_path": file_path,
            "type": "module",
            "code": source,
            "start_line": 1,
            "end_line": len(source.splitlines()),
        })
    js_chunks = llm_chunking(chunks)
    return js_chunks,tree

def split_large_chunks(code: str, max_lines: int = 200) -> List[str]:
    lines = code.splitlines()
    sub_chunks = []
    for i in range(0, len(lines), max_lines):
        sub_chunk = "\n".join(lines[i:i + max_lines])
        sub_chunks.append(sub_chunk)
    return sub_chunks

def llm_chunking(chunks: List[dict]) -> List[dict]:
    llm= ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    PROMPT = """
        You are an expert frontend software engineer.

        Your task is to split the following JavaScript / React source code
        into SMALL, SEMANTIC chunks.

        Each chunk must represent ONE clear responsibility, such as:
        - API calls
        - state management (hooks, reducers)
        - UI rendering (JSX)
        - event handlers
        - utility/helper logic

        Rules:
        - Do NOT modify the code
        - Do NOT invent or rewrite code
        - Do NOT explain anything
        - Do NOT repeat code across chunks
        - Prefer multiple small chunks over one large chunk
        - Return VALID JSON only (no markdown, no comments)

        Output format:
        [
        {{
            "title": "short, specific semantic title",
            "code": "exact code snippet"
        }}
        ]

        Source code:
        ----------------
        {code}
        ----------------
        """
    llm_chunks = []
    for chunk in chunks:
        if len(chunk["code"].splitlines()) < 200:
            llm_chunks.append(chunk)
            continue
        else:
            for sub_chunk in split_large_chunks(chunk["code"]):
                prompt = PROMPT.format(code=sub_chunk)
                response = llm.invoke(
                    [HumanMessage(content=prompt)]
                )
        try:
            semantic_chunks = json.loads(response.content.strip())
            for sem_chunk in semantic_chunks:
                llm_chunks.append({
                    "name": chunk["name"],
                    "file_path": chunk["file_path"],
                    "type": chunk["type"],
                    "code": sem_chunk["code"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "decorators": chunk.get("decorators", []),
                })
        except Exception:
            print(f"LLM chunking failed for chunk: {chunk['name']}")
            continue
    return llm_chunks
