#!/usr/bin/env python3
"""Build limits.csv from manifest.json"""

import json
import os


def main():
    # Read manifest.json from config directory
    manifest_path = "config/manifest.json"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Extract stage data
    stages = []
    for stage in manifest["stages"]:
        stages.append({
            "name": stage["name"],
            "limit": stage["limit"],
            "window_s": stage["window_s"]
        })

    # Sort by limit descending, then by name ascending
    stages.sort(key=lambda s: (-s["limit"], s["name"]))

    # Create report directory if it doesn't exist
    os.makedirs("report", exist_ok=True)

    # Write CSV file
    csv_path = "report/limits.csv"
    with open(csv_path, "w", newline="") as f:
        # Write header
        f.write("stage,limit,window_s\n")

        # Write data rows
        for stage in stages:
            f.write(f"{stage['name']},{stage['limit']},{stage['window_s']}\n")


if __name__ == "__main__":
    main()
