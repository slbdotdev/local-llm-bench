#!/usr/bin/env python3
"""Reference solution for t5-error-recovery. Run with the sandbox as the working directory:

    python solve.py

Never copied into a trial sandbox. It performs the reference edits with plain file
operations - the point of the reference is the end state, not the tool route - and writes the
reference deliverable.
"""
import json
import os

EDITS = []
DELIVERABLE = "ceiling.txt"
TEXT = "ceiling: 1792\nas_of: 2034-02-17\n"


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
