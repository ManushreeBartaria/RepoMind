import os
import git
from pathlib import Path
import ast
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs

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


#ast parser for python files
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


#ast parser for java files
def send_to_java_paser(cleaned_files):
    java_files=[]
    for files in cleaned_files:
        extension=files.suffix.lower()
        if extension==".java":
            java_files.append(files)
    return java_files 

JAVA_LANGUAGE = Language(tsjava.language())

def java_ast_parser(file_path: Path):
    chunks = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        parser = Parser()
        parser.set_language(JAVA_LANGUAGE)
        tree = parser.parse(bytes(file_content, "utf-8"))

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return chunks

    
    def walk(node):
        if node.type == "class_declaration":
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1

            chunks.append({
                "name": file_path.stem,
                "type": "Class",
                "code": "\n".join(file_content.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })

        elif node.type in ("method_declaration", "constructor_declaration"):
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            
            #extract method name
            method_name = None  
            for child in node.children:
                if child.type == "identifier":
                    method_name = file_content[
                child.start_byte : child.end_byte
            ]
                break

            chunks.append({
                "name": method_name,
                "type": "Method",
                "code": "\n".join(file_content.splitlines()[start - 1:end]),
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
            "code": file_content,
            "start_line": 1,
            "end_line": len(file_content.splitlines())
        })

    return chunks
   

# ast parser for javascript files
def send_to_js_parser(cleaned_files):
    js_files = []
    for files in cleaned_files:
        extension = files.suffix.lower()
        if extension in (".js", ".jsx", ".ts", ".tsx"):
            js_files.append(files)
    return js_files

JS_LANGUAGE = Language(tsjs.language()) 

def js_ast_parser(file_path: Path):
    chunks = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        parser = Parser()
        parser.set_language(JS_LANGUAGE)
        tree = parser.parse(bytes(file_content, "utf-8"))

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return chunks

    def walk(node):
        # function / method
        if node.type in ("function_declaration", "method_definition"):
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1

            func_name = None
            for child in node.children:
                if child.type == "identifier":
                    func_name = file_content[
                        child.start_byte : child.end_byte
                    ]
                    break

            chunks.append({
                "name": func_name,
                "type": "Function",
                "code": "\n".join(file_content.splitlines()[start - 1:end]),
                "start_line": start,
                "end_line": end,
            })

        # class
        elif node.type == "class_declaration":
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1

            class_name = None
            for child in node.children:
                if child.type == "identifier":
                    class_name = file_content[
                        child.start_byte : child.end_byte
                    ]
                    break

            chunks.append({
                "name": class_name,
                "type": "Class",
                "code": "\n".join(file_content.splitlines()[start - 1:end]),
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
            "code": file_content,
            "start_line": 1,
            "end_line": len(file_content.splitlines())
        })

    return chunks

        
        
if __name__ == "__main__":
    file_name=cloning("https://github.com/ManushreeBartaria/TrickIT.git")
    file_path="cloned_files/"+file_name
    cleaned_files=clean_files(Path(file_path))
    files=send_to_parser(cleaned_files)
    
    all_chunks = []
    
    py_files = send_to_parser(cleaned_files)
    for file in py_files:
        chunks = ast_parser(file)
        all_chunks.extend(chunks)  

    java_files=send_to_java_paser(cleaned_files)
    for file in java_files:
        chunks = java_ast_parser(file)
        all_chunks.extend(chunks)
        
    js_files = send_to_js_parser(cleaned_files)
    for file in js_files:
        chunks = js_ast_parser(file)
        all_chunks.extend(chunks)
        
    print("Total chunks extracted:", len(all_chunks))

    # Optional: see sample output
    for chunk in all_chunks[:5]:
        print("\n---")
        print("Name:", chunk["name"])
        print("Type:", chunk["type"])
        print("Lines:", chunk["start_line"], "-", chunk["end_line"])