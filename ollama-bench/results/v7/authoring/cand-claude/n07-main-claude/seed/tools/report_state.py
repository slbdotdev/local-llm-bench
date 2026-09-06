"""Print the custody schedule this pipeline is currently enforcing.

The schedule is not stored anywhere. It is resolved, every time the pipeline assembles, from
the stage modules: a module whose `CUSTODY_POOL` is `-none-` roots a custody pool and declares
that pool's period in `CUSTODY_DAYS`. This tool reads the modules the same way and prints what
it finds, so that an operator can see what is in force without assembling anything.

The modules are read as text rather than imported. Importing them would assemble the pipeline,
which is not something an audit tool has any business doing.

This output is what the platform enforces. A schedule written into a document is a copy taken
on the day somebody retyped it; where a document disagrees with this table, the document is
behind and this table is right.

What this tool does NOT print is which stages are in which pool. That is a property of each
stage's own module, it is written there and nowhere else on purpose, and printing a second
copy of it here would be the same mistake the pool merge was cleaning up.
"""
import hashlib
import json
import os
import re

MANIFEST = os.path.join("config", "manifest.json")
POOL = re.compile(r"^CUSTODY_POOL = \"(.*?)\"\s*$", re.M)
DAYS = re.compile(r"^CUSTODY_DAYS = (\d+)\s*$", re.M)
REVISION = re.compile(r"^CUSTODY_REVISION = \"(.*?)\"\s*$", re.M)
ROOT = "-none-"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    man = json.loads(read(MANIFEST))
    package = man["package"]
    revision = "unknown"
    init = os.path.join("src", package, "__init__.py")
    if os.path.isfile(init):
        m = REVISION.search(read(init))
        if m:
            revision = m.group(1)

    schedule = {}
    for stage in man["stages"]:
        src = os.path.join("src", package, stage["module"] + ".py")
        text = read(src)
        pool = POOL.search(text)
        if not pool or pool.group(1) != ROOT:
            continue
        days = DAYS.search(text)
        if not days:
            continue
        schedule[stage["name"]] = int(days.group(1))

    body = "\n".join("%s=%d" % (k, schedule[k]) for k in sorted(schedule))
    fingerprint = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]

    rule = "=" * 74
    print("%s custody state report" % man["project"])
    print("source: the stage modules under src/%s/, read at the moment this ran" % package)
    print(rule)
    print("This is the schedule the platform enforces. Where a document disagrees with it,")
    print("the document is behind and this table is right.")
    print("")
    print("schedule revision in force: %s" % revision)
    print("")
    print("%-24s %8s" % ("custody pool", "days"))
    print("%-24s %8s" % ("-" * 24, "-" * 8))
    for name in sorted(schedule):
        print("%-24s %8d" % (name, schedule[name]))
    print("")
    print("%d custody pools over %d stages." % (len(schedule), len(man["stages"])))
    print("Which stages are in which pool is not printed here and is not written down")
    print("anywhere: each stage's module names the stage it inherits its pool from, in")
    print("CUSTODY_POOL, and following that chain to a pool root is how a stage's period is")
    print("worked out. See docs/custody-policy.md.")
    print(rule)
    print("schedule fingerprint: %s" % fingerprint)


if __name__ == "__main__":
    main()
