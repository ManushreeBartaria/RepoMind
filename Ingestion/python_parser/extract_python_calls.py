import ast
from pathlib import Path

def extract_python_calls(chunks,tree,file_name):
    relations=[]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                relations.append({
                    "from": file_name,
                    "to": alias.name,
                    "type": "import",
                    "language": "python",
                    "line": node.lineno,
                    "confidence": "explicit"
                })

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                relations.append({
                    "from": file_name,
                    "to": f"{module}.{alias.name}",
                    "type": "import",
                    "language": "python",
                    "line": node.lineno,
                    "confidence": "explicit"
                })

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    parent = base.id
                elif isinstance(base, ast.Attribute):
                    parent = base.attr
                else:
                    parent = ast.dump(base)

                relations.append({
                    "from": node.name,
                    "to": parent,
                    "type": "inherits",
                    "language": "python",
                    "confidence": "syntactic"
                })

   
    for node in ast.walk(tree):
        if not hasattr(node, "lineno"):
            continue

        for chunk in chunks:
            if not (chunk["start_line"] <= node.lineno <= chunk["end_line"]):
                continue
            caller = chunk["name"]
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    callee = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    callee = node.func.attr
                else:
                    callee = ast.dump(node.func)

                relations.append({
                    "from": caller,
                    "to": callee,
                    "type": "call",
                    "language": "python",
                    "line": node.lineno,
                    "confidence": "syntactic"
                })
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                relations.append({
                    "from": caller,
                    "to": node.func.id,
                    "type": "instantiates",
                    "language": "python",
                    "line": node.lineno,
                    "confidence": "heuristic"
                })

            if isinstance(node, ast.Return):
                relations.append({
                    "from": caller,
                    "to": "return",
                    "type": "returns",
                    "language": "python",
                    "line": node.lineno,
                    "confidence": "explicit"
                })

    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    deco = decorator.id
                elif isinstance(decorator, ast.Attribute):
                    deco = decorator.attr
                else:
                    deco = ast.dump(decorator)

                relations.append({
                    "from": node.name,
                    "to": deco,
                    "type": "decorated_by",
                    "language": "python",
                    "confidence": "explicit"
                })

    return relations

    