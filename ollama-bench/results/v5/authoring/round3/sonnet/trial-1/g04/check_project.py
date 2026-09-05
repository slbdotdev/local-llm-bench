#!/usr/bin/env python3
"""Small public checker for the repair exercise."""
import importlib.util
import sys


def load():
    spec = importlib.util.spec_from_file_location("reconcile", "src/reconcile.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def findings(path):
    import ast
    text = open(path, encoding="utf-8").read()
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        if len(line.rstrip("\r")) > 100:
            out.append((number, "line longer than 100 characters"))
        if "== None" in line or "!= None" in line:
            out.append((number, "use an identity check for None"))
        if line.strip() == "except:":
            out.append((number, "bare except"))
    try:
        ast.parse(text, filename=path)
    except SyntaxError as exc:
        out.append((exc.lineno or 1, "syntax error"))
    return out


def main():
    problems = findings("src/reconcile.py")
    try:
        mod = load()
        report = mod.reconcile()
        expected_keys = {"total_usd", "by_account", "by_tax_code",
                         "accepted_ids", "accepted_count"}
        if set(report) != expected_keys:
            problems.append((0, "report keys"))
        if report["accepted_count"] != len(report["accepted_ids"]):
            problems.append((0, "count does not match IDs"))
        if report["total_usd"] != sum(report["by_account"].values(), mod.Decimal("0")):
            problems.append((0, "account total"))
        if report["total_usd"] <= 0:
            problems.append((0, "close is empty"))
        rendered = mod.format_report(report)
        if len(rendered.splitlines()) != 5 or not rendered.startswith("TOTAL "):
            problems.append((0, "report rendering"))
    except Exception as exc:
        problems.append((0, "program error: " + type(exc).__name__))
    if problems:
        for line, message in problems:
            print("src/reconcile.py:%s: %s" % (line or "?", message))
        return 1
    print("CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
