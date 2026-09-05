#!/usr/bin/env python3
"""Build Capacity Planning's stage limits report.

Reads config/manifest.json and writes report/limits.csv, covering every
stage in the manifest except those on Platform Reliability's on-call rota
(docs/operations.md), per the policy in docs/policy/capacity-report.md.
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "config", "manifest.json")
OPERATIONS_PATH = os.path.join(ROOT, "docs", "operations.md")
REPORT_DIR = os.path.join(ROOT, "report")
REPORT_PATH = os.path.join(REPORT_DIR, "limits.csv")


def load_platform_reliability_stages(path):
    """Parse the on-call column of the operations.md table and return the
    set of stage names owned by Platform Reliability."""
    stages = set()
    with open(path, "r", newline="") as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0].lower() == "stage":
            in_table = True
            continue
        if not in_table:
            continue
        if re.match(r"^:?-+:?$", cells[0]):
            continue
        stage_name, on_call_team = cells[0], cells[3]
        if on_call_team == "Platform Reliability":
            stages.add(stage_name)
    return stages


def main():
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    platform_reliability_stages = load_platform_reliability_stages(OPERATIONS_PATH)

    rows = []
    for stage in manifest["stages"]:
        if stage["name"] in platform_reliability_stages:
            continue
        rows.append((stage["name"], stage["limit"], stage["window_s"]))

    rows.sort(key=lambda r: (-r[1], r[0]))

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", newline="\n") as f:
        f.write("stage,limit,window_s\n")
        for name, limit, window_s in rows:
            f.write("{0},{1},{2}\n".format(name, limit, window_s))


if __name__ == "__main__":
    main()
