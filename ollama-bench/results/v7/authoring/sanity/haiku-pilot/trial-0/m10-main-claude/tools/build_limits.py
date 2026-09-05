#!/usr/bin/env python3
"""Generate the capacity planning limits report from the manifest."""

import json
import os
from pathlib import Path

# Stages on Platform Reliability's rota (from docs/operations.md)
PLATFORM_RELIABILITY_STAGES = {
    "compaction",
    "dispatch",
    "attestation",
    "rollup",
    "checkpoint"
}


def main():
    # Read the manifest
    manifest_path = Path("config/manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Extract and filter stages
    rows = []
    for stage in manifest["stages"]:
        if stage["name"] not in PLATFORM_RELIABILITY_STAGES:
            rows.append({
                "stage": stage["name"],
                "limit": stage["limit"],
                "window_s": stage["window_s"]
            })
    
    # Sort by limit descending, then by name ascending
    rows.sort(key=lambda x: (-x["limit"], x["stage"]))
    
    # Create report directory if it doesn't exist
    report_dir = Path("report")
    report_dir.mkdir(exist_ok=True)
    
    # Write CSV file
    csv_path = report_dir / "limits.csv"
    with open(csv_path, "w") as f:
        f.write("stage,limit,window_s\n")
        for row in rows:
            f.write(f"{row['stage']},{row['limit']},{row['window_s']}\n")


if __name__ == "__main__":
    main()
