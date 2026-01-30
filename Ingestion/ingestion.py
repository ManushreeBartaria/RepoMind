import git
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
import pickle
import hashlib

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from Ingestion.python_parser.parse_python_files import ast_parser
from Ingestion.python_parser.extract_python_calls import extract_python_calls

from Ingestion.java_parser.parse_java_files import java_ast_parser
from Ingestion.java_parser.extract_java_calls import extract_java_calls

from Ingestion.js_parser.parse_js_files import js_ast_parser
from Ingestion.js_parser.extract_js_calls import extract_js_calls

from Ingestion.graph_making import create_graph
from Ingestion.bridge import infer_frontend_backend_bridges

load_dotenv()


# =========================================================
# Cache management
# =========================================================
def get_repo_hash(git_url: str) -> str:
    """Create a unique hash for this repo URL"""
    return hashlib.md5(git_url.encode()).hexdigest()[:8]


def is_already_processed(git_url: str) -> bool:
    """Check if this exact repo has been processed before"""
    repo_hash = get_repo_hash(git_url)
    cache_file = Path(f"cache/{repo_hash}.done")
    graph_file = Path("code_graph.pkl")
    chroma_dir = Path("RepoMind/db/chroma_db")
    
    return cache_file.exists() and graph_file.exists() and chroma_dir.exists()


def mark_as_processed(git_url: str):
    """Mark this repo as processed"""
    repo_hash = get_repo_hash(git_url)
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    
    cache_file = cache_dir / f"{repo_hash}.done"
    cache_file.write_text(git_url)


# =========================================================
# Repo cloning
# =========================================================
def clone_repo(git_url: str) -> Path:
    repo_name = git_url.split("/")[-1].replace(".git", "")
    clone_path = Path("cloned_files") / repo_name

    if not clone_path.exists():
        git.Repo.clone_from(git_url, clone_path)

    return clone_path


# =========================================================
# File filtering
# =========================================================
def clean_files(path: Path) -> List[Path]:
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
        ".gitignore", "__init__.py"
    }

    files = []

    if path.is_dir():
        if path.name in IGNORED_DIRS:
            return []
        for child in path.iterdir():
            files.extend(clean_files(child))

    elif path.is_file():
        if (
            path.name not in IGNORED_FILES
            and path.suffix.lower() not in IGNORED_EXTENSIONS
        ):
            files.append(path)

    return files


# =========================================================
# Language separation
# =========================================================
def split_by_language(files: List[Path]):
    py, java, js = [], [], []

    for f in files:
        ext = f.suffix.lower()
        if ext == ".py":
            py.append(f)
        elif ext == ".java":
            java.append(f)
        elif ext in {".js", ".jsx", ".ts", ".tsx"}:
            js.append(f)

    return py, java, js


# =========================================================
# Vector document creation
# =========================================================
def to_langchain_docs(
    chunks: List[dict],
    repo_root: Path
) -> List[Document]:
    docs = []

    for c in chunks:
        docs.append(
            Document(
                page_content=c["code"],
                metadata={
                    "chunk_id": f"{c['file_path']}::{c['name']}",
                    "file": str(c["file_path"].relative_to(repo_root)),
                    "title": c["name"],
                    "type": c["type"],
                    "language": c.get("language"),
                    "params": ", ".join(c.get("params", [])),
                    "start_line": c["start_line"],
                    "end_line": c["end_line"],
                },
            )
        )

    return docs


# =========================================================
# 🚀 MAIN INGESTION ENTRY (BACKEND CALLS THIS)
# =========================================================
def run_ingestion(git_url: str) -> Dict:
    """
    PURE INGESTION PIPELINE WITH CACHING.

    Builds and persists:
    - code_graph.pkl
    - chroma vector DB

    Skips processing if already done for this exact repo URL.
    """

    # Check cache first
    if is_already_processed(git_url):
        print(f"✅ Repository already processed, skipping ingestion")
        repo_name = git_url.split("/")[-1].replace(".git", "")
        return {
            "repository": repo_name,
            "cached": True,
            "message": "Using cached results"
        }

    print(f"🔄 Processing repository: {git_url}")

    repo_root = clone_repo(git_url)
    repo_name = repo_root.name

    files = clean_files(repo_root)
    py_files, java_files, js_files = split_by_language(files)

    all_chunks = []
    all_relations = []

    # ---------------- Python ----------------
    for f in py_files:
        chunks, tree = ast_parser(f)
        for c in chunks:
            c["language"] = "python"
        all_chunks.extend(chunks)

        file_id = str(f.relative_to(repo_root))
        all_relations.extend(
            extract_python_calls(chunks, tree, file_id)
        )

    # ---------------- Java ----------------
    for f in java_files:
        chunks, tree = java_ast_parser(f)
        for c in chunks:
            c["language"] = "java"
        all_chunks.extend(chunks)

        file_id = str(f.relative_to(repo_root))
        all_relations.extend(
            extract_java_calls(chunks, tree, file_id)
        )

    # ---------------- JavaScript ----------------
    for f in js_files:
        chunks, tree = js_ast_parser(f)
        for c in chunks:
            c["language"] = "javascript"
        all_chunks.extend(chunks)

        file_id = str(f.relative_to(repo_root))
        all_relations.extend(
            extract_js_calls(chunks, tree, file_id)
        )

    # ---------------- Cross-language bridges ----------------
    bridge_edges = infer_frontend_backend_bridges(
        all_chunks,
        all_relations
    )
    all_relations.extend(bridge_edges)

    # ---------------- Persist artifacts ----------------
    create_graph(all_chunks, all_relations)

    docs = to_langchain_docs(all_chunks, repo_root)

    # Clear old chroma DB if exists
    chroma_dir = Path("RepoMind/db/chroma_db")
    if chroma_dir.exists():
        import shutil
        shutil.rmtree(chroma_dir)

    Chroma.from_documents(
        documents=docs,
        embedding=HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        ),
        persist_directory="RepoMind/db/chroma_db",
        collection_metadata={"hnsw:space": "cosine"},
    )

    # Mark as processed
    mark_as_processed(git_url)

    print(f"✅ Ingestion complete for {repo_name}")

    return {
        "repository": repo_name,
        "chunks": len(all_chunks),
        "relations": len(all_relations),
        "python_files": len(py_files),
        "java_files": len(java_files),
        "js_files": len(js_files),
        "cached": False
    }