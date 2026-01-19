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
from langchain.schema import HumanMessage, Document

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

    return chunks


<<<<<<< HEAD
#apply llm for frontened ingestion

FRONTEND_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}

GEMINI_MODEL="gemini-1.5-flash"
TEMPERATURE=0

##LLM Initialization
llm = ChatGoogleGenerativeAI(model_name=GEMINI_MODEL, temperature=TEMPERATURE)

# LLM Prompt
SEMANTIC_CHUNK_PROMPT = """
You are an expert software engineer.

Split the following frontend source code into smaller semantic chunks.
Each chunk must represent ONE clear responsibility or intent
(e.g. API calls, state management, UI rendering, event handlers).

Rules:
- Do NOT modify the code
- Do NOT invent new code
- Keep chunks meaningful
- Return VALID JSON only

Output format:
[
  {
    "title": "short semantic title",
    "code": "exact code snippet"
  }
]

Source code:
----------------
{code}
----------------
"""



#gemini semantic chunking function
def semantic_chunk_with_llm(code: str) -> List[dict]:
    prompt = SEMANTIC_CHUNK_PROMPT.format(code=code)

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    try:
        return json.loads(response.content)
    except Exception:
        return []
    
# CONVERT TO LANGCHAIN DOCS

def semantic_chunks_to_documents(
    chunks: List[dict],
    file_path: Path
) -> List[Document]:

    docs = []
    for chunk in chunks:
        docs.append(
            Document(
                page_content=chunk["code"],
                metadata={
                    "file": str(file_path),
                    "title": chunk["title"],
                    "semantic": True
                }
            )
        )
    return docs

# MAIN PIPELINE
def process_chunks(
    file_path: Path,
    ast_chunks: List[dict]
) -> List[Document]:
    """
    AST → (Gemini only for JS/TS) → LangChain Documents
    """

    documents = []

    
    # BACKEND FILES (NO LLM)
    if file_path.suffix.lower() not in FRONTEND_EXTENSIONS:
        for chunk in ast_chunks:
            documents.append(
                Document(
                    page_content=chunk["code"],
                    metadata={
                        "file": str(file_path),
                        "type": chunk.get("type"),
                        "semantic": False
                    }
                )
            )
        return documents
    
 # FRONTEND FILES (GEMINI)
   
    for chunk in ast_chunks:
        semantic_chunks = semantic_chunk_with_llm(chunk["code"])

        # fallback if Gemini fails
        if not semantic_chunks:
            documents.append(
                Document(
                    page_content=chunk["code"],
                    metadata={
                        "file": str(file_path),
                        "fallback": True
                    }
                )
            )
        else:
            documents.extend(
                semantic_chunks_to_documents(
                    semantic_chunks,
                    file_path
                )
            )

    return documents
=======
>>>>>>> 05a87220ff3e6546fdfc04492e3533c5c905519c
        
        
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

    # Optional: see sample output
    for chunk in all_chunks[:44]:
        print("\n---")
        print("Name:", chunk["name"])
        print("Type:", chunk["type"])
        print("Lines:", chunk["start_line"], "-", chunk["end_line"])
        print("Code:\n", chunk["code"])