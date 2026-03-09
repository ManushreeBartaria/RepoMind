import ast
from pathlib import Path
from typing import List, Dict

def ast_parser(file_path: Path):
    chunks = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        tree = ast.parse(file_content)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return chunks
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent
    def get_chunk_type(node):
        if isinstance(node, ast.ClassDef):
            return "class"
        if isinstance(node, ast.AsyncFunctionDef):
            if isinstance(getattr(node, "parent", None), ast.ClassDef):
                return "async_method"
            return "async_function"
        if isinstance(node, ast.FunctionDef):
            if isinstance(getattr(node, "parent", None), ast.ClassDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "staticmethod":
                            return "static_method"
                        if decorator.id == "classmethod":
                            return "class_method"
                return "method"
            return "function"
        return "unknown"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            code = ast.get_source_segment(file_content, node)
            
            # Extract decorators for bridge inference
            decorators = []
            if hasattr(node, "decorator_list"):
                for decorator in node.decorator_list:
                    deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                    decorators.append(deco_str)
            
            chunks.append({
                "name": node.name,
                "file_path": file_path,
                "type": get_chunk_type(node),
                "code": code,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "decorators": decorators,
            })
    if not chunks:
        chunks.append({
            "name": file_path.stem,
            "file_path": file_path,
            "type": "module",
            "code": file_content,
            "start_line": 1,
            "end_line": len(file_content.splitlines()),
        })
    return chunks,tree