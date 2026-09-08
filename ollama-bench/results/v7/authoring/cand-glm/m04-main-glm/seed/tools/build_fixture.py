"""Build the complete regression fixture from a caller-supplied review.

This script reads no stage document or module. The caller must supply exactly one row for every
manifest stage, including both dates and the already-derived inclusion decision. The script only
checks the review's shape and manifest membership, then writes those 19 rows in manifest order.
`tools/run_checks.py` independently traverses the material and compares the fixture by digest.
Neither tool prints a stage name, date, decision, or row count.

    python tools/build_fixture.py <path-to-your-complete-review>

The review CSV header is `stage,declared_date,effective_date,included`; `included` is `yes` or
`no`, and all 19 manifest stages must appear exactly once.
"""
import csv
import json
import os
import sys

CUTOVER = "2034-04-01"


def _read_review(path):
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != ["stage", "declared_date", "effective_date", "included"]:
            raise ValueError("review header must be stage,declared_date,effective_date,included")
        rows = list(reader)
    out = []
    for r in rows:
        row = {k: (r.get(k) or "").strip() for k in reader.fieldnames}
        if not all(row.values()) or row["included"] not in ("yes", "no"):
            raise ValueError("each review row needs two dates and yes/no inclusion")
        out.append(row)
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
    try:
        review = _read_review(review_path)
    except (OSError, ValueError) as exc:
        print("invalid review: %s" % exc)
        return 2
    names = [r["stage"] for r in review]
    unknown = sorted(set(names) - set(all_names))
    if unknown:
        print("review contains a stage outside the manifest")
        return 2
    if names != all_names:
        print("review does not contain one row per manifest stage")
        return 2
    by_name = {r["stage"]: r for r in review}
    out = os.path.join("data", "regression-fixture.csv")
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write("stage,declared_date,effective_date,included\n")
        for name in all_names:
            r = by_name[name]
            fh.write("%s,%s,%s,%s\n" % tuple(r[k] for k in
                                              ("stage", "declared_date", "effective_date", "included")))
    print("fixture written to %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
