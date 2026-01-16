import os
import git
from pathlib import Path
import ast

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
    for file in cleaned_files:
        extension=file.suffix.lower()
        if extension==".py":
            py_files.append(file)
    return py_files

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

        
        
if __name__ == "__main__":
    file_name=cloning("https://github.com/ManushreeBartaria/TrickIT.git")
    file_path="cloned_files/"+file_name
    cleaned_files=clean_files(Path(file_path))
    files=send_to_parser(cleaned_files)
    chunks=[]
    for file in files:
       chunks=ast_parser(file)
       print("total chunks:",len(chunks))  

