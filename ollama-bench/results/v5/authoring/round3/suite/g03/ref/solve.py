"""Apply the complete public-builder migration to the supplied tree."""

import ast
from pathlib import Path


def _rewrite(path):
    text = path.read_text(encoding="utf-8")
    text = text.replace("make_tag", "make_badge")
    text = text.replace('>>> make_badge("Ada", "warm")',
                        '>>> make_badge("Ada", tone="warm")')
    try:
        tree = ast.parse(text)
    except SyntaxError:
        path.write_text(text, encoding="utf-8")
        return

    class Calls(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if len(node.args) >= 2 and (
                    name == "make_badge" or
                    isinstance(node.args[1], ast.Name) and node.args[1].id == "tone" or
                    isinstance(node.args[1], ast.Attribute)
                    and isinstance(node.args[1].value, ast.Name)
                    and node.args[1].value.id == "self"
                    and node.args[1].attr == "tone"):
                second = node.args.pop(1)
                node.keywords.insert(0, ast.keyword(arg="tone", value=second))
            return node

    tree = Calls().visit(tree)
    ast.fix_missing_locations(tree)
    output = ast.unparse(tree)
    output = output.replace("def make_badge(label, tone=DEFAULT_TONE):",
                            "def make_badge(label, *, tone=DEFAULT_TONE):")
    path.write_text(output + "\n", encoding="utf-8")


for _root in (Path("badges"), Path("tests")):
    for _path in sorted(_root.rglob("*.py")):
        _rewrite(_path)
