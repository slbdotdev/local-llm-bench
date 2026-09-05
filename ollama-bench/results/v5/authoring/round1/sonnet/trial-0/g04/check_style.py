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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            positional = list(node.args.posonlyargs) + list(node.args.args)
            defaults = [None] * (len(positional) - len(node.args.defaults))
            defaults += list(node.args.defaults)
            for default in defaults:
                if isinstance(default, (ast.Dict, ast.List, ast.Set)):
                    out.append((default.lineno,
                                "mutable default argument; use None and initialize"))
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append((node.lineno, "bare except; catch Exception explicitly"))
        if isinstance(node, ast.Compare):
            values = [node.left] + list(node.comparators)
            for value, op in zip(values[1:], node.ops):
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    if isinstance(op, (ast.Is, ast.IsNot)):
                        out.append((node.lineno, "use equality for string values"))
                if isinstance(value, ast.Constant) and isinstance(value.value, bool):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        out.append((node.lineno, "use a boolean expression, not comparison to bool"))
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip(" \t") != line:
            out.append((number, "trailing whitespace"))
        if len(line) > 88:
            out.append((number, "line longer than 88 characters"))
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) == 2 else "policy.py"
    for line, message in findings(path):
        print("%s:%s: %s" % (path, line, message))
    if not findings(path):
        print("CLEAN")
