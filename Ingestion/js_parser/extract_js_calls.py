from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
from pathlib import Path
from typing import List


def extract_js_calls(chunks, tree, file_name):
    relations = []
    def walk(node):
        start_line = node.start_point[0] + 1 if node.start_point else None
        if node.type == "import_statement":
            relations.append({
                "from": file_name,
                "to": node.text.decode("utf-8"),
                "type": "import",
                "language": "javascript",
                "confidence": "explicit"
            })
        if node.type == "class_declaration":
            class_name = None
            parent_class = None

            for child in node.children:
                if child.type == "identifier":
                    class_name = child.text.decode("utf-8")
                if child.type == "class_heritage":
                    for g in child.children:
                        if g.type == "identifier":
                            parent_class = g.text.decode("utf-8")

            if class_name and parent_class:
                relations.append({
                    "from": class_name,
                    "to": parent_class,
                    "type": "inherits",
                    "language": "javascript",
                    "confidence": "explicit"
                })
        for chunk in chunks:
            if start_line and chunk["start_line"] <= start_line <= chunk["end_line"]:
                caller = chunk["name"]

                if node.type == "call_expression":
                    for child in node.children:
                        if child.type == "identifier":
                            relations.append({
                                "from": caller,
                                "to": child.text.decode("utf-8"),
                                "type": "call",
                                "language": "javascript",
                                "confidence": "syntactic"
                            })

                if node.type == "new_expression":
                    for child in node.children:
                        if child.type == "identifier":
                            relations.append({
                                "from": caller,
                                "to": child.text.decode("utf-8"),
                                "type": "instantiates",
                                "language": "javascript",
                                "confidence": "explicit"
                            })
        if node.type == "decorator":
            relations.append({
                "from": file_name,
                "to": node.text.decode("utf-8"),
                "type": "decorated_by",
                "language": "javascript",
                "confidence": "explicit"
            })

        for child in node.children:
            walk(child)
    walk(tree.root_node)
    return relations
