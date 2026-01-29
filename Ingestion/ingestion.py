import os
import git
from typing import List
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from RepoMind.Ingestion.python_parser.parse_python_files import ast_parser
from RepoMind.Ingestion.python_parser.extract_python_calls import extract_python_calls

from RepoMind.Ingestion.java_parser.parse_java_files import java_ast_parser
from RepoMind.Ingestion.java_parser.extract_java_calls import extract_java_calls

from RepoMind.Ingestion.js_parser.parse_js_files import js_ast_parser
from RepoMind.Ingestion.js_parser.extract_js_calls import extract_js_calls

from RepoMind.Ingestion.graph_making import create_graph
from RepoMind.Ingestion.bridge import infer_frontend_backend_bridges

load_dotenv()


def cloning(git_link: str) -> str:
    repo_name = git_link.split("/")[-1].replace(".git", "")
    clone_path = Path("cloned_files") / repo_name

    if not clone_path.exists():
        git.Repo.clone_from(git_link, clone_path)

    return repo_name


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

    cleaned = []

    if path.is_dir():
        if path.name in IGNORED_DIRS:
            return []
        for child in path.iterdir():
            cleaned.extend(clean_files(child))

    elif path.is_file():
        if (
            path.name not in IGNORED_FILES
            and path.suffix.lower() not in IGNORED_EXTENSIONS
        ):
            cleaned.append(path)

    return cleaned


def send_to_parser(files: List[Path]):
    py_files, java_files, js_files = [], [], []

    for file in files:
        ext = file.suffix.lower()
        if ext == ".py":
            py_files.append(file)
        elif ext == ".java":
            java_files.append(file)
        elif ext in (".js", ".jsx", ".ts", ".tsx"):
            js_files.append(file)

    return py_files, java_files, js_files


def langchain_documents(
    chunks: List[dict],
    repo_root: Path
) -> List[Document]:
    docs = []

    for chunk in chunks:
        docs.append(
            Document(
                page_content=chunk["code"],
                metadata={
                    "chunk_id": f"{chunk['file_path']}::{chunk['name']}",
                    "file": str(chunk["file_path"].relative_to(repo_root)),
                    "title": chunk["name"],
                    "type": chunk["type"],
                    "language": chunk.get("language"),
                    "params": ", ".join(chunk.get("params", [])),
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                },
            )
        )

    return docs


def embeddings_and_vectorDB(
    docs: List[Document],
    persist_directory: str = "RepoMind/db/chroma_db",
):
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    return vector_store


if __name__ == "__main__":
    repo_name = cloning("https://github.com/ManushreeBartaria/TrickIT.git")
    repo_root = Path("cloned_files") / repo_name

    cleaned_files = clean_files(repo_root)
    py_files, java_files, js_files = send_to_parser(cleaned_files)

    all_chunks = []
    all_relations = []

    for file in py_files:
        chunks, ast_tree = ast_parser(file)
        for c in chunks:
            c["language"] = "python"
        all_chunks.extend(chunks)

        file_id = str(file.relative_to(repo_root))
        all_relations.extend(
            extract_python_calls(chunks, ast_tree, file_id)
        )

    for file in java_files:
        chunks, ast_tree = java_ast_parser(file)
        for c in chunks:
            c["language"] = "java"
        all_chunks.extend(chunks)

        file_id = str(file.relative_to(repo_root))
        all_relations.extend(
            extract_java_calls(chunks, ast_tree, file_id)
        )

    for file in js_files:
        chunks, ast_tree = js_ast_parser(file)
        for c in chunks:
            c["language"] = "javascript"
        all_chunks.extend(chunks)

        file_id = str(file.relative_to(repo_root))
        all_relations.extend(
            extract_js_calls(chunks, ast_tree, file_id)
        )

    # Phase: Infer frontend-backend semantic bridges
    # This creates HTTP_CALL edges between frontend API calls and backend handlers
    bridge_relations = infer_frontend_backend_bridges(all_chunks, all_relations)
    all_relations.extend(bridge_relations)

    graph = create_graph(all_chunks, all_relations)

    documents = langchain_documents(all_chunks, repo_root)
    vector_store = embeddings_and_vectorDB(documents)
