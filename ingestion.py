import os
import json                     
from typing import List        
import git
from pathlib import Path
import ast
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

from dotenv import load_dotenv

load_dotenv()
def cloning(git_link):
    repo_name = git_link.split("/")[-1].replace(".git", "")
    if not os.path.exists("cloned_files/" + repo_name):
        git.Repo.clone_from(git_link, "cloned_files/" + repo_name)
    return repo_name

def clean_files(path: Path):
    IGNORED_DIRS = {
    ".git", "venv", "__pycache__", "node_modules",
    "dist", "build", ".cache"
}
    IGNORED_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".svg",
        ".mp3", ".mp4", ".wav",
        ".pdf", ".zip", ".exe", ".bin",
        ".env", ".lock", ".log", ".csv"
    }
    IGNORED_FILES = {
        ".gitignore","__init__.py"
    }
    cleaned_files = []
    if path.is_dir():
        if path.name in IGNORED_DIRS:
            return []
        for child in path.iterdir():
            cleaned_files.extend(clean_files(child))
    elif path.is_file():
        if (
            path.name not in IGNORED_FILES and
            path.suffix.lower() not in IGNORED_EXTENSIONS
        ):
            cleaned_files.append(path)
    return cleaned_files

def send_to_parser(cleaned_files):
    py_files=[]
    java_files=[]
    js_files=[]
    for file in cleaned_files:
        extension=file.suffix.lower()
        if extension==".py":
            py_files.append(file)
        elif extension==".java":
            java_files.append(file)
        elif extension in (".js", ".jsx", ".ts", ".tsx"):
            js_files.append(file)
    return py_files, java_files, js_files

def ast_parser(file_path: Path):
    chunks=[]
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        tree = ast.parse(file_content)
    except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            code=ast.get_source_segment(file_content, node)
            chunks.append({
                "name": node.name,
                "type": type(node).__name__,
                "code":code,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                })
    if not chunks:
        chunks.append({
                "name": file_path.stem,
                "type": "Module",
                "code": file_content,
                "start_line": 1,
                "end_line": len(file_content.splitlines()),
                })
    return chunks  

JAVA_LANGUAGE = Language(tsjava.language())
def java_ast_parser(file_path: Path):
    chunks = []
    seen_nodes = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    parser = Parser(JAVA_LANGUAGE)
    tree = parser.parse(source.encode("utf-8"))


    ANNOTATION_USAGE_NODES = {
        "annotation",
        "marker_annotation",
        "annotation_argument_list",
    }


    def extract_direct_identifier(node):
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def walk(node):
        if id(node) in seen_nodes:
            return
        seen_nodes.add(id(node))
        if node.type in ANNOTATION_USAGE_NODES:
            return

        start = node.start_point[0] + 1
        end = node.end_point[0] + 1
        if node.type == "annotation_type_declaration":
            name = extract_direct_identifier(node)
            chunks.append({
                "name": name,
                "type": "Annotation",
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })

        elif node.type == "class_declaration":
            name = extract_direct_identifier(node)
            chunks.append({
                "name": name or file_path.stem,
                "type": "Class",
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })
        elif node.type in ("method_declaration", "constructor_declaration") and node.parent.type=="class_body":
            name = extract_direct_identifier(node)
            chunks.append({
                "name": name,
                "type": "Method",
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })

        for child in node.children:
            walk(child)

    walk(tree.root_node)
    if not chunks:
        chunks.append({
            "name": file_path.stem,
            "type": "Module",
            "code": source,
            "start_line": 1,
            "end_line": len(source.splitlines()),
        })

    return chunks


JS_LANGUAGE =Language(tsjs.language())
def js_ast_parser(file_path: Path):
    chunks = []
    js_chunks=[]
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

    def walk(node):
        if id(node) in seen_nodes:
            return
        seen_nodes.add(id(node))

        start = node.start_point[0] + 1
        end = node.end_point[0] + 1
        if node.type == "function_declaration":
            name = extract_identifier(node)
            chunks.append({
                "name": name,
                "type": "Function",
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })
        elif node.type == "variable_declarator":
            name = extract_identifier(node)
            for child in node.children:
                if child.type == "arrow_function":
                    chunks.append({
                        "name": name,
                        "type": "ArrowFunction",
                        "code": "\n".join(source.splitlines()[start - 1:end]),
                        "start_line": start,
                        "end_line": end,
                    })
                    break
        elif node.type == "class_declaration":
            name = extract_identifier(node)
            chunks.append({
                "name": name,
                "type": "Class",
                "code": "\n".join(source.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })

        for child in node.children:
            walk(child)

    walk(tree.root_node)
    if not chunks:
        chunks.append({
            "name": file_path.stem,
            "type": "Module",
            "code": source,
            "start_line": 1,
            "end_line": len(source.splitlines())
        })
    js_chunk=llm_chunking(chunks)
    return js_chunk

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
                    "type": chunk["type"],
                    "code": sem_chunk["code"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                })
        except Exception:
            print(f"LLM chunking failed for chunk: {chunk['name']}")
            continue
    return llm_chunks


def langchain_documents(chunks: List[dict], file_path: Path
) -> List[Document]:
    docs = []
    for chunk in chunks:
        docs.append(
            Document(
                page_content=chunk["code"],
                metadata={
                    "file": str(file_path),
                    "title": chunk["name"],
                    "type": chunk["type"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"]
                }
            )
        )
    return docs
        
        
if __name__ == "__main__":
    file_name=cloning("https://github.com/ManushreeBartaria/TrickIT.git")
    file_path="cloned_files/"+file_name
    cleaned_files=clean_files(Path(file_path))
    files=send_to_parser(cleaned_files)
    
    all_chunks = []
    
    py_files, java_files, js_files = send_to_parser(cleaned_files)
    for file in py_files:
        chunks = ast_parser(file)
        all_chunks.extend(chunks) 
    for file in java_files:
        chunks = java_ast_parser(file)
        all_chunks.extend(chunks)
    for file in js_files:
        chunks = js_ast_parser(file)
        all_chunks.extend(chunks)     
    
    print("Total chunks extracted:", len(all_chunks))
    documents = langchain_documents(all_chunks, Path(file_path))
    print("Total LangChain documents created:", len(documents))
    for doc in documents[:44]:
        print("\n---")
        print("Metadata:", doc.metadata)
        print("Content:\n", doc.page_content)