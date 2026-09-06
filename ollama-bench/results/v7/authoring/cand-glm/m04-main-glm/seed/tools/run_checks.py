"""Verify the regression fixture against an independent, from-scratch sweep. Writes nothing.

This is the real check: the grader runs this file itself and trusts nothing else. It reads
every stage's own document AND every stage's own module directly, for every stage -- a stage
is "provisional" exactly when its document's `declared_verified_on` disagrees with its
module's `ROLLOUT_VERIFIED_ON`, and there is no way to know which stages disagree without
comparing both values for all of them. It compares the result, row for row, against whatever
is actually on disk at `data/regression-fixture.csv`. It prints only `OK` or `FAIL`, never a
stage name or a row count: this file exists to verify a claim, not to hand one over.

Reading is deliberately tolerant of incidental whitespace in the fixture (a blank line,
trailing spaces, the line-ending style) since none of that is part of what the fixture
asserts; only the sequence of stage names is.
"""
import json
import os
import re
import sys

CUTOVER = "2034-04-01"


def _declared_verified_on(root, name):
    path = os.path.join(root, "docs", name + ".md")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^\| `declared_verified_on` \| ([\d-]+) \|", text, re.M)
    return m.group(1) if m else None


def _verified_on(root, package, module):
    path = os.path.join(root, "src", package, module + ".py")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r'^ROLLOUT_VERIFIED_ON = "([\d-]+)"', text, re.M)
    return m.group(1) if m else "0000-00-00"


def compute(root="."):
    with open(os.path.join(root, "config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    package = man["package"]
    included = []
    excluded = []
    for st in man["stages"]:
        name = st["name"]
        declared = _declared_verified_on(root, name)
        effective = _verified_on(root, package, st["module"])
        provisional = (declared != effective)
        if provisional and effective >= CUTOVER:
            excluded.append(name)
        else:
            included.append(name)
    return included, excluded


def main():
    path = os.path.join("data", "regression-fixture.csv")
    if not os.path.isfile(path):
        print("FAIL")
        return 1
    with open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh.read().splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines or lines[0].lower() != "stage":
        print("FAIL")
        return 1
    rows = lines[1:]
    expected_rows, _excluded = compute(".")
    if rows != expected_rows:
        print("FAIL")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
