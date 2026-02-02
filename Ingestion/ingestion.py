from email.parser import Parser
import os
import json                     
from typing import List,Set       
import git
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
from RepoMind.Ingestion.python_parser.parse_python_files import ast_parser as ast_parser
from RepoMind.Ingestion.python_parser.extract_python_calls import extract_python_calls
from RepoMind.Ingestion.java_parser.extract_java_calls import extract_java_calls
from RepoMind.Ingestion.js_parser.extract_js_calls import extract_js_calls
from RepoMind.Ingestion.java_parser.parse_java_files import java_ast_parser as java_ast_parser
from RepoMind.Ingestion.js_parser.parse_js_files import js_ast_parser as js_ast_parser
from pathlib import Path
from RepoMind.Ingestion.graph_making import create_graph

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


def langchain_documents(chunks: List[dict], file_path: Path
) -> List[Document]:
    docs = []
    for chunk in chunks:  
        docs.append(
            Document(
                page_content=chunk["code"],
                metadata={
                    "chunk_id": f"{chunk['file_path']}::{chunk['name']}",
                    "file": str(chunk["file_path"].relative_to(file_path)),
                    "title": chunk["name"],
                    "type": chunk["type"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"]
                }
            )
        )
    return docs

def embeddings_and_vectorDB(docs: List[Document],persist_directory: str = "RepoMind/db/chroma_db"):
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_store = Chroma.from_documents(
        documents=docs,                    
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    vector_store.persist()             
    return vector_store
    
        
        
if __name__ == "__main__":
    file_name=cloning("https://github.com/ManushreeBartaria/TrickIT.git")
    file_path="cloned_files/"+file_name
    cleaned_files=clean_files(Path(file_path))
    files=send_to_parser(cleaned_files)
    
    all_chunks = []
    all_relations=[]
    
    py_files, java_files, js_files = send_to_parser(cleaned_files)
    for file in py_files:
        chunks,ast_tree = ast_parser(file)
        all_chunks.extend(chunks) 
        all_relations.extend(extract_python_calls(chunks,ast_tree,file.name))
    for file in java_files:
        chunks,ast_tree = java_ast_parser(file)
        all_chunks.extend(chunks)
        all_relations.extend(extract_java_calls(chunks,ast_tree,file.name))
    for file in js_files:
        chunks,ast_tree = js_ast_parser(file)
        all_chunks.extend(chunks)     
        all_relations.extend(extract_js_calls(chunks,ast_tree,file.name))
    graph=create_graph(all_chunks,all_relations)    
    documents = langchain_documents(all_chunks, Path(file_path))
    vectorStore=embeddings_and_vectorDB(documents)
    