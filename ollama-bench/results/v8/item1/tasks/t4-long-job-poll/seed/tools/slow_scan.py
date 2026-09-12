#!/usr/bin/env python3
"""Walk the first nine stages, one per second, and print a result token.

    python3 tools/slow_scan.py

It takes about nine seconds on purpose: this is the shape of job that has to
be started in the background and polled, not waited on in the foreground. A
PARTIAL line is printed part way through so that a half-read of the output is
detectable; PARTIAL is never the answer.
"""
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
    MANIFEST = json.load(fh)
STAGES = [s["name"] for s in MANIFEST["stages"]][:9]


def tok(kind, names):
    return hashlib.sha256(
        "|".join([MANIFEST["project"], kind] + list(names)).encode("utf-8")
    ).hexdigest()[:8]


for i, name in enumerate(STAGES):
    print("scanning %s" % name, flush=True)
    if i == 4:
        print("PARTIAL %s %d  (not the answer; the scan is unfinished)"
              % (tok("partial", STAGES[:4]), 4), flush=True)
    time.sleep(1.0)
print("RESULT %s %d" % (tok("final", STAGES), len(STAGES)), flush=True)
