#!/usr/bin/env python3
"""The round-3 authoring table, generated from the candidates on disk.

    python3 r3/authoring_report.py            # print the table
    python3 r3/authoring_report.py --stamp    # write it into results/v7/authoring-r3-2026-09-08.md

A table typed by hand drifts from the directory it describes within one revision — the same
failure `stamp_notes.py` and `composition.py` exist to prevent, one level up. So every number
here is measured now: material from each `MANIFEST.json`, the load-bearing set out of each
`test.py` by `ast.literal_eval`, and the expected coverage by re-deriving each spec's own
sweep set against its seed.

The stamped block sits between `<!-- BEGIN GENERATED r3 TABLE -->` and its END marker.
"""
import argparse
import ast
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
V7 = os.path.dirname(AUTHORING)
sys.path.insert(0, AUTHORING)

PAGE = os.path.join(V7, "authoring-r3-2026-09-08.md")
BEGIN = "<!-- BEGIN GENERATED r3 TABLE -->"
END = "<!-- END GENERATED r3 TABLE -->"


def load_bearing(test_py):
    with open(test_py, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "LOAD_BEARING":
                    return ast.literal_eval(node.value)
    return []


def rows():
    out = []
    for n in sorted(os.listdir(os.path.join(HERE, "specs"))):
        if not (n.startswith("n") and n.endswith(".py")):
            continue
        spec = importlib.import_module("r3.specs." + n[:-3])
        cand = os.path.join(AUTHORING, "cand-" + spec.FAMILY, spec.SLOT)
        if not os.path.isdir(cand):
            continue
        man = json.load(open(os.path.join(cand, "MANIFEST.json"), encoding="utf-8"))
        lb = load_bearing(os.path.join(cand, "test.py"))
        files = man.get("files") or {}
        common = importlib.import_module("r3.common")
        corpus = common.Corpus(os.path.join(cand, "seed"))
        ctx = {"seed": os.path.join(cand, "seed"), "corpus": corpus, "spec": spec}
        ctx["facts"] = spec.facts(ctx)
        sweep = sorted(set(spec.sweep_paths(ctx)))
        sweep_tok = sum(files.get(p, 0) for p in sweep)
        lb_tok = sum(files.get(p, 0) for p in set(p["path"] for p in lb))
        groups = ctx["facts"]["groups"]
        out.append({
            "slot": spec.SLOT, "family": spec.FAMILY, "mode": spec.MODE,
            "tokens": man["material_tokens"], "files": man["seed_files"],
            "lb_paths": len(set(p["path"] for p in lb)),
            "lb_hops": len(set(p["hop"] for p in lb)),
            "lb_tokens": lb_tok,
            "sweep_files": len(sweep), "sweep_tokens": sweep_tok,
            "coverage": round(100.0 * sweep_tok / man["material_tokens"], 1),
            "floor": round(100.0 * lb_tok / man["material_tokens"], 1),
            "subchecks": 3 + len(groups) + (1 if getattr(spec, "editable", None)
                                            and spec.editable(ctx) else 0) + 1,
            "deliverable": spec.DELIVERABLE,
            "keys": len(ctx["facts"]["keys"]),
            "editable": len(spec.editable(ctx)) if hasattr(spec, "editable") else 0,
            "checks": [g["name"] for g in groups],
        })
    return out


def table(rs):
    L = ["| slot | mode | family | material | files | load-bearing | hops | sweep | expected coverage | deliverable | subchecks |",
         "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |"]
    for r in rs:
        L.append("| `%s` | %d | %s | %s | %d | %d | %d | %d files / %s tok | **%.1f%%** | `%s` | %d |"
                 % (r["slot"], r["mode"], r["family"], "{:,}".format(r["tokens"]), r["files"],
                    r["lb_paths"], r["lb_hops"], r["sweep_files"],
                    "{:,}".format(r["sweep_tokens"]), r["coverage"], r["deliverable"],
                    r["subchecks"]))
    if rs:
        tok = sum(r["tokens"] for r in rs)
        cov = sum(r["sweep_tokens"] for r in rs)
        L.append("| **%d slots** | | | **%s** | | | | | **%.1f%%** | | |"
                 % (len(rs), "{:,}".format(tok), 100.0 * cov / tok))
    return "\n".join(L)


def checks_table(rs):
    L = ["| slot | what the checker checks, beyond shape and integrity |",
         "| --- | --- |"]
    for r in rs:
        L.append("| `%s` | %s |" % (r["slot"], "; ".join(r["checks"])))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", action="store_true")
    a = ap.parse_args()
    rs = rows()
    body = table(rs) + "\n\n" + checks_table(rs)
    if not a.stamp:
        print(body)
        return 0
    if not os.path.exists(PAGE):
        print("no page at %s yet" % PAGE)
        return 1
    text = open(PAGE, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print("the page carries no generated-table markers")
        return 1
    head, rest = text.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + BEGIN + "\n\n" + body + "\n\n" + END + tail)
    print("stamped %d row(s) into %s" % (len(rs), PAGE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
