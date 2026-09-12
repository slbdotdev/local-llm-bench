#!/usr/bin/env python3
"""Check that the four places that record the attestation handle limit agree.

    python3 tools/verify_attestation.py

Prints one verdict line - `-> consistent` or `-> inconsistent` - and a token.
Reports; never edits.
"""
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def one(path, pattern):
    with open(os.path.join(ROOT, *path.split("/")), encoding="utf-8") as fh:
        m = re.search(pattern, fh.read(), re.M)
    return int(m.group(1)) if m else None


module = one("src/futtock/attestation_core.py", r"^DEFAULT_ATTESTATION_LIMIT = (\d+)$")
doc = one("docs/attestation.md", r"^\| `limit` \| (\d+) \|")
test = one("tests/test_attestation.py", r"engine\.limit == (\d+)")
with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
    stages = {s["name"]: s for s in json.load(fh)["stages"]}
manifest = stages["attestation"]["limit"]

values = [module, manifest, doc, test]
verdict = "consistent" if len(set(values)) == 1 and None not in values else "inconsistent"
print("attestation: module=%s manifest=%s doc=%s test=%s -> %s"
      % (module, manifest, doc, test, verdict))
print("TOKEN %s" % hashlib.sha256(
    ("attestation|" + "|".join(str(v) for v in values)).encode("utf-8")).hexdigest()[:8])
