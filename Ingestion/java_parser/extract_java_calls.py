from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
from pathlib import Path
from typing import List

def extract_java_calls(chunks, tree, file_name):
    relations = []
    def walk(node):
        if node.type == "import_declaration":
            text = node.text.decode("utf-8")
            relations.append({
                "from": file_name,
                "to": text.replace("import", "").replace(";", "").strip(),
                "type": "import",
                "language": "java",
                "confidence": "explicit"
            })
        if node.type == "class_declaration":
            class_name = None
            for child in node.children:
                if child.type == "identifier":
                    class_name = child.text.decode("utf-8")
            for child in node.children:
                if child.type == "superclass":
                    for g in child.children:
                        if g.type == "type_identifier":
                            relations.append({
                                "from": class_name,
                                "to": g.text.decode("utf-8"),
                                "type": "inherits",
                                "language": "java",
                                "confidence": "explicit"
                            })
        if node.type in ("method_declaration", "constructor_declaration"):
            method_name = None
            for child in node.children:
                if child.type == "identifier":
                    method_name = child.text.decode("utf-8")
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            for chunk in chunks:
                if chunk["start_line"] <= start <= chunk["end_line"]:
                    caller = chunk["name"]
                    for sub in node.children:
                        if sub.type == "method_invocation":
                            for c in sub.children:
                                if c.type == "identifier":
                                    relations.append({
                                        "from": caller,
                                        "to": c.text.decode("utf-8"),
                                        "type": "call",
                                        "language": "java",
                                        "confidence": "syntactic"
                                    })
        if node.type == "object_creation_expression":
            for child in node.children:
                if child.type == "type_identifier":
                    relations.append({
                        "from": file_name,
                        "to": child.text.decode("utf-8"),
                        "type": "instantiates",
                        "language": "java",
                        "confidence": "explicit"
                    })
        for child in node.children:
            walk(child)
    walk(tree.root_node)
    return relations
