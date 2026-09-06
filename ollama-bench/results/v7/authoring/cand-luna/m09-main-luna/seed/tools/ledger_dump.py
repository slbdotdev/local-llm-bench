"""Print the ceiling-migration ledger, one block per stage, in manifest order.

Reads `data/migration-ledger.csv`, which is an event log and not a table of stages: a stage
has a `measured`, a `proposed`, a `migrated` and a `counter_signed` event, and a few stages
have an attempt that was recorded and then annulled by a `voided` event.

This tool resolves each stage to its one completed migration -- the `migrated` event that is
counter-signed and not annulled -- and prints it on the stage's `-> migrated_on` line.

The ledger records dates and never a ceiling. A ledger that carried the numbers as well would
go stale against the modules the day either changed, and the project has been bitten by a
number with five copies once already.
"""
import csv
import json
import os
import re

LEDGER = os.path.join("data", "migration-ledger.csv")
MANIFEST = os.path.join("config", "manifest.json")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def load():
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def resolve(rows):
    """stage -> the date of its completed, counter-signed, un-annulled migration."""
    signed, annulled = {}, {}
    for r in rows:
        m = DATE.search(r["detail"] or "")
        if not m:
            continue
        if r["event"] == "counter_signed":
            signed.setdefault(r["stage"], {})[m.group(1)] = (r["recorded_on"], r["actor"])
        elif r["event"] == "voided":
            annulled.setdefault(r["stage"], set()).add(m.group(1))
    out = {}
    for r in rows:
        if r["event"] != "migrated":
            continue
        d = r["recorded_on"]
        if d in annulled.get(r["stage"], ()):
            continue
        if d not in signed.get(r["stage"], {}):
            continue
        out[r["stage"]] = (d,) + signed[r["stage"]][d]
    return out


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)
    order = [s["name"] for s in man["stages"]]
    modules = dict((s["name"], s["module"]) for s in man["stages"])
    rows = load()
    by_stage = {}
    for r in rows:
        by_stage.setdefault(r["stage"], []).append(r)
    done = resolve(rows)

    rule = "=" * 74
    print("%s ceiling migration ledger" % man["project"])
    print("source: %s" % LEDGER)
    print(rule)
    print("%d events over %d stages, in manifest order. An attempt that no `counter_signed`"
          % (len(rows), len(order)))
    print("event names, or that a `voided` event annuls, is not a completed migration and is")
    print("not the date any ruling reads. Dates only: this ledger has never carried a ceiling.")
    for i, name in enumerate(order):
        print("")
        print("[%02d/%02d] %s  (module %s)" % (i + 1, len(order), name, modules[name]))
        for r in by_stage.get(name, []):
            print("  %s  %-15s %-16s %s"
                  % (r["recorded_on"], r["event"], r["actor"], r["detail"]))
        if name in done:
            d, signed_on, actor = done[name]
            print("  -> migrated_on = %s   (counter-signed %s by %s)" % (d, signed_on, actor))
        else:
            print("  -> migrated_on = none   (no completed, counter-signed migration)")
    print("")
    print(rule)
    print("%d of %d stages have a completed, counter-signed migration." % (len(done), len(order)))


if __name__ == "__main__":
    main()
