"""Verify the complete fixture by digest, without handing over the answer.

The checker reads every stage's own document and module, constructs only a SHA-256 digest of
the 19 canonical rows, and compares it with a digest of the supplied CSV. It prints only OK or
FAIL: it never prints a stage name, date, decision, rule, or row count. There is deliberately
no `compute()` or answer-returning helper to import. The fixture's four columns are all part of
the digest input, including both dates and the inclusion decision.
"""
import csv
import hashlib
import json
import os
import re
import sys

CUTOVER = "2034-04-01"


def _material_digest(root):
    with open(os.path.join(root, "config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    h = hashlib.sha256()
    for st in man["stages"]:
        name = st["name"]
        with open(os.path.join(root, "docs", name + ".md"), encoding="utf-8") as fh:
            doc = fh.read()
        with open(os.path.join(root, "src", man["package"], st["module"] + ".py"),
                  encoding="utf-8") as fh:
            module = fh.read()
        dm = re.search(r"^\| `declared_verified_on` \| ([0-9-]+) \|", doc, re.M)
        mm = re.search(r'^ROLLOUT_VERIFIED_ON = "([0-9-]+)"$', module, re.M)
        if not dm or not mm:
            return None
        declared, effective = dm.group(1), mm.group(1)
        included = "yes" if not (declared != effective and effective >= CUTOVER) else "no"
        h.update(("|".join((name, declared, effective, included)) + "\n").encode("utf-8"))
    return h.hexdigest()


def _fixture_digest(path):
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [line for line in fh if line.strip()]
        rows = [[cell.strip() for cell in row] for row in csv.reader(lines)]
    if not rows or rows[0] != ["stage", "declared_date", "effective_date", "included"]:
        return None
    data = rows[1:]
    if len(data) != 19 or any(len(row) != 4 for row in data):
        return None
    if any(any(not cell for cell in row) for row in data):
        return None
    h = hashlib.sha256()
    for row in data:
        if row[3] not in ("yes", "no"):
            return None
        h.update(("|".join(row) + "\n").encode("utf-8"))
    return h.hexdigest()


def main():
    path = os.path.join("data", "regression-fixture.csv")
    if not os.path.isfile(path):
        print("FAIL")
        return 1
    try:
        supplied = _fixture_digest(path)
        expected = _material_digest(".")
    except (OSError, UnicodeError, ValueError, csv.Error):
        supplied = expected = None
    if not supplied or supplied != expected:
        print("FAIL")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
