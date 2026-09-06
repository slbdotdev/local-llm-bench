"""Build the regression fixture from a caller-supplied review of provisional stages.

This script performs no sweep of its own: it does not read any stage's document or module. It
combines `config/manifest.json`'s stage list with a review file the caller supplies -- one row
per stage the caller has determined is provisional (its document's declared date and its own
module's effective date disagree), together with
that stage's own module's `ROLLOUT_VERIFIED_ON` date -- and applies the cutover rule
mechanically. Getting the review right is the caller's job; `tools/run_checks.py` checks the
result independently, from scratch, against the real tree, so this script does not print a row
count or a stage name -- it has no way to know which of its inputs are correct.

    python tools/build_fixture.py <path-to-your-provisional-stages-review>

The review file is CSV with a header `stage,rollout_date`, one data row per stage you have
determined is provisional. A stage not listed is treated as not provisional and is
never excluded, whatever its module says.
"""
import csv
import json
import os
import sys

CUTOVER = "2034-04-01"


def _read_review(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        name = (r.get("stage") or "").strip()
        date = (r.get("rollout_date") or "").strip()
        if name:
            out[name] = date
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: build_fixture.py <path-to-your-provisional-stages-review>")
        return 2
    review_path = sys.argv[1]
    if not os.path.isfile(review_path):
        print("no review file at %s" % review_path)
        return 2
    with open(os.path.join("config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    all_names = [st["name"] for st in man["stages"]]
    review = _read_review(review_path)
    unknown = sorted(n for n in review if n not in all_names)
    if unknown:
        print("review names stage(s) not in the manifest: %s" % ", ".join(unknown))
        return 2
    excluded = set(n for n, date in review.items() if date >= CUTOVER)
    included = [n for n in all_names if n not in excluded]
    out = os.path.join("data", "regression-fixture.csv")
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write("stage\n")
        for name in included:
            fh.write(name + "\n")
    print("fixture written to %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
