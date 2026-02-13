from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path
import uuid
import pickle
import subprocess

from ..core.state import state
from ..schemas.ingest import (
    IngestRequest,
    IngestStartResponse,
    IngestStatusResponse,
    FileTreeNode
)
from Ingestion.ingestion import run_ingestion

router = APIRouter()


def build_tree(path: Path) -> dict:
    if path.is_file():
        return {
            "name": path.name,
            "path": str(path),
            "type": "file",
            "children": []
        }

    return {
        "name": path.name,
        "path": str(path),
        "type": "folder",
        "children": [
            build_tree(p)
            for p in path.iterdir()
            if not p.name.startswith(".")
        ]
    }


def ingestion_task(repo_id: str, git_url: str):
    try:
        run_ingestion(git_url)

        with open("code_graph.pkl", "rb") as f:
            state.graph = pickle.load(f)

        state.repos[repo_id]["status"] = "completed"

    except Exception as e:
        state.repos[repo_id]["status"] = "failed"
        state.repos[repo_id]["error"] = str(e)


@router.post("/repo", response_model=IngestStartResponse)
def start_ingestion(payload: IngestRequest, bg: BackgroundTasks):
    repo_id = str(uuid.uuid4())
    repo_name = payload.git_url.split("/")[-1].replace(".git", "")
    repo_path = Path("cloned_files") / repo_name

    # Just check if folder exists and build tree
    tree = build_tree(repo_path) if repo_path.exists() else None

    state.repos[repo_id] = {
        "status": "processing",
        "tree": tree
    }

    # Start ingestion in background
    bg.add_task(ingestion_task, repo_id, payload.git_url)

    return {
        "repo_id": repo_id,
        "file_tree": tree
    }


@router.get("/status/{repo_id}")
def get_status(repo_id: str):
    repo = state.repos.get(repo_id)
    if not repo:
        raise HTTPException(404, "Repo not found")

    return {
        "status": repo["status"]
    }

@router.get("/health")
def heatlth_check():
    return {"status":"ok"}    