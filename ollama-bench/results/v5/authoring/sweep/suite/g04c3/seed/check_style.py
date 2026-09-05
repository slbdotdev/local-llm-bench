#!/usr/bin/env python3
import ast
import sys


def findings(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    out = []
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        return [(exc.lineno or 1, "syntax error")]
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    values = [node.left] + list(node.comparators)
                    if any(isinstance(x, ast.Constant) and isinstance(x.value, bool)
                           for x in values):
                        out.append((node.lineno, "use a boolean expression, not comparison to bool"))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "StringIO" and not any(k.arg == "newline" for k in node.keywords):
                out.append((node.lineno, "StringIO must declare newline explicitly"))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (node.func.attr == "writer" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "csv"
                    and not any(k.arg == "quoting" for k in node.keywords)):
                out.append((node.lineno, "CSV writer must declare quoting explicitly"))
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip(" \t") != line:
            out.append((number, "trailing whitespace"))
        if len(line) > 88:
            out.append((number, "line longer than 88 characters"))
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) == 2 else "report.py"
    for line, message in findings(path):
        print("%s:%s: %s" % (path, line, message))
    if not findings(path):
        print("CLEAN")
