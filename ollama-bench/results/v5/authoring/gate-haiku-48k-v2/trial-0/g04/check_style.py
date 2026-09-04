#!/usr/bin/env python3
import ast
import sys


def findings(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip(" \t") != line:
            out.append((number, "trailing whitespace"))
        if len(line) > 88:
            out.append((number, "line longer than 88 characters"))
        if "== None" in line or "!= None" in line:
            out.append((number, "use an identity check for None"))
        if line.strip() == "except:":
            out.append((number, "bare except"))
    try:
        ast.parse(text, filename=path)
    except SyntaxError as exc:
        out.append((exc.lineno or 1, "syntax error"))
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) == 2 else "invoice.py"
    for line, message in findings(path):
        print("%s:%s: %s" % (path, line, message))
    if not findings(path):
        print("CLEAN")
