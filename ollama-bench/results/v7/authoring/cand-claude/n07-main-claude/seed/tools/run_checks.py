"""Validate a filed custody correction set. Writes nothing; exits 0 only when it is accepted.

    python3 tools/run_checks.py

Reads `data/doc-corrections.csv`, which a reviewer writes: one row per component document
whose `custody_days` is stale, three fields --

    <stage>,<the stage that roots its custody pool>,<the period it should state>

Every check below is a check on what the reviewer filed. This tool does not work out which
documents are stale and does not say: see `docs/policy-records/` on why a checker that answers
the question it is asked to verify is verifying itself.

The fingerprint is taken over each corrected stage's whole custody chain -- the path from the
stage to the root of its pool, as `a>b>c|days` -- and not over the stage and the root alone.
Whether a reviewer named the right pool for a stage is therefore settled by the fingerprint,
over the set as a whole, and is never reported row by row: a checker that says which single
row is wrong can be asked one stage at a time until it has given up the whole answer.
"""
import hashlib
import json
import os
import re
import sys

MANIFEST = os.path.join("config", "manifest.json")
CORRECTIONS = os.path.join("data", "doc-corrections.csv")
LOCK = os.path.join("data", "custody-review.lock")
POOL = re.compile(r"^CUSTODY_POOL = \"(.*?)\"\s*$", re.M)
DAYS = re.compile(r"^CUSTODY_DAYS = (\d+)\s*$", re.M)
ROOT = "-none-"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def rows():
    """The filed corrections, tolerantly: blank lines, an optional header and stray spaces
    around a field are all a reviewer's file and none of them is a finding."""
    out = []
    for line in read(CORRECTIONS).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [c.strip() for c in line.split(",")]
        if len(parts) == 3 and parts[0].lower() == "stage":
            continue
        out.append(parts)
    return out


def doc_days(stage):
    m = re.search(r"^\| `custody_days` \| (\d+) \|",
                  read(os.path.join("docs", stage + ".md")), re.M)
    return int(m.group(1)) if m else None


def chain(package, modules, stage):
    """The custody chain from `stage` to the root of its pool, as a list of stage names.

    Follows `CUSTODY_POOL` from module to module, exactly as docs/custody-policy.md describes
    it. Returns None for a chain that names a stage the manifest does not, that loops, or
    that never reaches a root; none of those can happen in a tree this tool would accept.
    """
    out, seen, cur = [], set(), stage
    while True:
        if cur in seen or cur not in modules:
            return None
        seen.add(cur)
        out.append(cur)
        m = POOL.search(read(os.path.join("src", package, modules[cur] + ".py")))
        if not m:
            return None
        if m.group(1) == ROOT:
            return out
        cur = m.group(1)


def main():
    failures = []
    if not os.path.isfile(CORRECTIONS):
        print("FAIL  no correction set has been filed at %s" % CORRECTIONS)
        print("CHECKS: fail")
        return 1

    man = json.loads(read(MANIFEST))
    package = man["package"]
    modules = dict((s["name"], s["module"]) for s in man["stages"])

    filed = rows()
    if not filed:
        failures.append("the filed correction set is empty")
    seen = set()
    clean = []
    for n, parts in enumerate(filed, 1):
        if len(parts) != 3:
            failures.append("row %d does not have three fields" % n)
            continue
        stage, pool, period = parts
        if stage not in modules:
            failures.append("row %d names %r, which is not a stage in the manifest"
                            % (n, stage))
            continue
        if stage in seen:
            failures.append("row %d names %r a second time" % (n, stage))
            continue
        seen.add(stage)
        if not period.isdigit():
            failures.append("row %d does not carry a whole number of days" % n)
            continue
        period = int(period)
        if pool not in modules:
            failures.append("row %d names the pool %r, which is not a stage" % (n, pool))
            continue
        text = read(os.path.join("src", package, modules[pool] + ".py"))
        m = POOL.search(text)
        if not m or m.group(1) != ROOT:
            failures.append("row %d names %r as a custody pool and %r does not root one"
                            % (n, pool, pool))
            continue
        d = DAYS.search(text)
        if not d or int(d.group(1)) != period:
            failures.append("row %d gives a period that is not the one %r's pool holds for"
                            % (n, pool))
            continue
        stated = doc_days(stage)
        if stated is None:
            failures.append("row %d names %r, whose document states no period" % (n, stage))
            continue
        if stated == period:
            failures.append("row %d restates what %r's document already says, so it is not "
                            "a correction" % (n, stage))
            continue
        ch = chain(package, modules, stage)
        if ch is None:
            failures.append("row %d names %r, whose custody chain does not reach a pool root"
                            % (n, stage))
            continue
        clean.append((ch, period))

    recorded = None
    for line in read(LOCK).splitlines():
        if line.startswith("corrections_sha256:"):
            recorded = line.split(":", 1)[1].strip()
    if recorded is None:
        failures.append("%s records no fingerprint" % LOCK)
    else:
        body = "\n".join(sorted("%s|%d" % (">".join(c), d) for c, d in clean))
        got = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if got != recorded:
            failures.append("the filed correction set does not match the fingerprint the "
                            "last review recorded")

    for f in failures:
        print("FAIL  %s" % f)
    if failures:
        print("CHECKS: fail")
        return 1
    print("OK    every filed row names a stage, a pool that roots one, and that pool's period")
    print("OK    every filed row corrects what its document states rather than restating it")
    print("OK    every corrected stage's custody chain resolves to a pool root")
    print("OK    the correction set matches the fingerprint recorded by the last review")
    print("CHECKS: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
