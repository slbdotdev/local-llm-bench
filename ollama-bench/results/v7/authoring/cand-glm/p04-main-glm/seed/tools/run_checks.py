"""Release verification for the latchbridge pipeline.

Replays every stage's intake journal under data/intake/ and compares the replayed held
count with the closing position recorded at the end of the stage's own document under
docs/. The replay starts at zero and takes each journal's rows in file order: an `admitted` row adds the
row's record count; a `released` row and a `reaped` row each subtract theirs. A stage's
check passes when the counter at the last row equals the declared row exactly.

Exits 0 when every stage's check passes and 1 when any check fails. The output carries
counts only; which stages failed is read by applying the replay to each stage's journal,
per docs/release-checklist.md. The tool writes nothing, so a verification answers the
same way every time it is run.
"""
import csv
import json
import os
import re
import sys

MANIFEST = os.path.join("config", "manifest.json")
INTAKE = os.path.join("data", "intake")


def replay(path):
    held = 0
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            n = int(row["records"])
            event = row["event"]
            if event == "admitted":
                held += n
            elif event in ("released", "reaped"):
                held -= n
            else:
                raise ValueError("unknown journal event %r in %s" % (event, path))
    return held


SECTION = "## Closing position"


def declared(stage):
    doc = os.path.join("docs", stage["name"] + ".md")
    with open(doc, encoding="utf-8") as fh:
        text = fh.read()
    head, sep, tail = text.partition(SECTION)
    if not sep:
        raise ValueError("no closing position section in %s" % doc)
    m = re.search(r"\d+", tail)
    if not m:
        raise ValueError("no closing position recorded in %s" % doc)
    return int(m.group())


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)
    failed = 0
    for st in man["stages"]:
        held = replay(os.path.join(INTAKE, st["name"] + ".csv"))
        if held != declared(st):
            failed += 1
    print("release verification for %s" % man["project"])
    print("stages checked: %d" % len(man["stages"]))
    print("checks failed: %d" % failed)
    print("result: %s" % ("OK" if failed == 0 else "FAILED"))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
