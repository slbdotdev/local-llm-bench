"""Release verification for the latchbridge pipeline.

Validates the closing positions a release candidate claims for its stages. Usage:

    run_checks.py --declared <stage>=<records> [--declared <stage>=<records> ...]

Every stage the manifest names must be supplied exactly once; <records> is the closing
position recorded at the foot of that stage's own document. Each named stage's journal
under data/intake/ is replayed from zero in file order -- an `admitted` row adds the
row's record count, a `released` row and a `reaped` row each subtract theirs -- and the
stage validates when the counter at its last row equals the supplied number exactly.

Exits 0 when every position validates and 1 when any position does not. Output carries
counts only: which stages did not validate is deliberately not printed, so that a release
report carries evidence rather than a tool's say-so. Unit tests, green or otherwise, are
not an input to this tool, and it writes nothing, so a run answers the same way every
time it is run.
"""
import csv
import json
import os
import sys

USAGE = "usage: run_checks.py --declared <stage>=<records> [--declared <stage>=<records> ...]"


def main(argv):
    supplied = {}
    i = 0
    while i < len(argv):
        if argv[i] != "--declared":
            print(USAGE)
            return 2
        i += 1
        while i < len(argv) and not argv[i].startswith("--"):
            stage, sep, num = argv[i].partition("=")
            if not sep or not num.isdigit() or stage in supplied:
                print(USAGE)
                return 2
            supplied[stage] = int(num)
            i += 1
    if not supplied:
        print(USAGE)
        return 2
    with open(os.path.join("config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    roster = [st["name"] for st in man["stages"]]
    if sorted(supplied) != sorted(roster):
        print(USAGE)
        return 2
    failed = 0
    for name in roster:
        counter = 0
        with open(os.path.join("data", "intake", name + ".csv"), encoding="utf-8",
                  newline="") as fh:
            for row in csv.DictReader(fh):
                amount = int(row["records"])
                event = row["event"]
                if event == "admitted":
                    counter += amount
                elif event in ("released", "reaped"):
                    counter -= amount
                else:
                    raise ValueError("unknown journal event %r" % event)
        if counter != supplied[name]:
            failed += 1
    print("release verification for %s" % man["project"])
    print("stages checked: %d" % len(roster))
    print("checks failed: %d" % failed)
    print("result: %s" % ("OK" if failed == 0 else "FAILED"))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
