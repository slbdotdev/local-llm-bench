#!/usr/bin/env python3
"""Print the cinder-crest quarantine timeline, oldest first.

    python tools/timeline_dump.py

Reads data/quarantine-timeline.csv and prints every entry on one line, sorted
by date, then batch, then kind. The CSV is the evidence copy; this printer only
formats it and never edits it.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "quarantine-timeline.csv")

KIND_LABELS = {
    "quarantined": "QUARANTINED",
    "requarantined": "RE-QUARANTINED",
    "lifted": "LIFTED",
    "annotation": "annotation",
}


def main():
    try:
        with open(CSV_PATH, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as exc:
        print("cannot read %s: %s" % (CSV_PATH, exc))
        return 1
    if not rows:
        print("timeline export at %s is empty" % CSV_PATH)
        return 1
    rows.sort(key=lambda r: (r["date"], r["batch"], r["kind"]))
    print("cinder-crest quarantine timeline - %d entries, %s to %s"
          % (len(rows), rows[0]["date"], rows[-1]["date"]))
    print("date        batch     stage           kind           detail")
    for r in rows:
        print("%s  %-8s  %-14s  %-13s  %s"
              % (r["date"], r["batch"], r["stage"], KIND_LABELS[r["kind"]], r["detail"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
