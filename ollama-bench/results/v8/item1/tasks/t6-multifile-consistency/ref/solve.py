#!/usr/bin/env python3
"""Reference solution for t6-multifile-consistency. Run with the sandbox as the working directory:

    python solve.py

Never copied into a trial sandbox. It performs the reference edits with plain file
operations - the point of the reference is the end state, not the tool route - and writes the
reference deliverable.
"""
import json
import os

EDITS = [
 {
  "name": "edit_file",
  "arguments": {
   "path": "src/futtock/attestation_core.py",
   "old": "DEFAULT_ATTESTATION_LIMIT = 96",
   "new": "DEFAULT_ATTESTATION_LIMIT = 160"
  }
 },
 {
  "name": "edit_file",
  "arguments": {
   "path": "config/manifest.json",
   "old": "      \"name\": \"attestation\",\n      \"module\": \"attestation_core\",\n      \"class\": \"AttestationGateway\",\n      \"limit\": 96,",
   "new": "      \"name\": \"attestation\",\n      \"module\": \"attestation_core\",\n      \"class\": \"AttestationGateway\",\n      \"limit\": 160,"
  }
 },
 {
  "name": "edit_file",
  "arguments": {
   "path": "docs/attestation.md",
   "old": "| `limit` | 96 | the largest number of handles held before the stage refuses new work |",
   "new": "| `limit` | 160 | the largest number of handles held before the stage refuses new work |"
  }
 },
 {
  "name": "edit_file",
  "arguments": {
   "path": "tests/test_attestation.py",
   "old": "engine.limit == 96",
   "new": "engine.limit == 160"
  }
 }
]
DELIVERABLE = "consistency-report.json"
TEXT = "{\n  \"paths\": [\n    \"config/manifest.json\",\n    \"docs/attestation.md\",\n    \"src/futtock/attestation_core.py\",\n    \"tests/test_attestation.py\"\n  ],\n  \"old\": 96,\n  \"new\": 160,\n  \"verified\": \"attestation: module=160 manifest=160 doc=160 test=160 -> consistent\"\n}\n"


def main():
    for call in EDITS:
        args = call["arguments"]
        path = os.path.join(*args["path"].split("/"))
        with open(path, "rb") as fh:
            data = fh.read().decode("utf-8")
        if call["name"] != "edit_file":
            raise SystemExit("reference only uses edit_file, not %s" % call["name"])
        if data.count(args["old"]) != 1:
            raise SystemExit("reference edit is not unique in %s (%d matches)"
                             % (args["path"], data.count(args["old"])))
        data = data.replace(args["old"], args["new"], 1)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(data)
    with open(os.path.join(*DELIVERABLE.split("/")), "w", encoding="utf-8", newline="") as fh:
        fh.write(TEXT)
    print("reference solution applied")


if __name__ == "__main__":
    main()
