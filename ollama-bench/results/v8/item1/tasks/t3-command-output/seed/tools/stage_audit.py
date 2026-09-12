#!/usr/bin/env python3
"""Report stages whose module limit disagrees with the manifest.

    python3 tools/stage_audit.py

A MISMATCH is a disagreement on `limit` only. A disagreement on `window_s` is
reported as NEAR and is not a mismatch: window_s is tuned per deployment and
the manifest value is advisory, which is why the two are separate lines.

Always exits 0, so the caller sees the output.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def const(module, name):
    path = os.path.join(ROOT, "src", PACKAGE, module + ".py")
    with open(path, encoding="utf-8") as fh:
        m = re.search(r"^%s = (\d+)$" % re.escape(name), fh.read(), re.M)
    return int(m.group(1)) if m else None


with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
    MANIFEST = json.load(fh)
PACKAGE = MANIFEST["package"]

mismatch, nearly = [], []
for stage in MANIFEST["stages"]:
    upper = stage["name"].upper()
    lim = const(stage["module"], "DEFAULT_%s_LIMIT" % upper)
    win = const(stage["module"], "DEFAULT_%s_WINDOW_S" % upper)
    if lim != stage["limit"]:
        mismatch.append((stage["name"], stage["limit"], lim))
    elif win != stage["window_s"]:
        nearly.append((stage["name"], stage["window_s"], win))

for name, want, got in mismatch:
    print("MISMATCH %s manifest=%s module=%s" % (name, want, got))
for name, want, got in nearly:
    print("NEAR %s window_s manifest=%s module=%s (not a mismatch)" % (name, want, got))
print("TOTAL %d" % len(mismatch))
digest = hashlib.sha256(
    "|".join([MANIFEST["project"]] + sorted(n for n, _, _ in mismatch)).encode("utf-8")
).hexdigest()[:8]
print("TOKEN %s" % digest)
sys.exit(0)
