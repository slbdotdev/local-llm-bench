"""Resolve the retention event history without changing it."""
import csv
import json
import os
import re

LEDGER = os.path.join("data", "retention-events.csv")
MANIFEST = os.path.join("config", "manifest.json")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
WINDOWS = re.compile(
    r"^- Window base: (\d+)\n- Declared remainder: (\d+)\n- Runtime remainder: (\d+)$",
    re.MULTILINE,
)


def load():
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def resolve(rows):
    signed, voided = {}, {}
    for row in rows:
        match = DATE.search(row["detail"] or "")
        if not match:
            continue
        if row["event"] == "countersigned":
            signed.setdefault(row["region"], set()).add(match.group(1))
        elif row["event"] == "voided":
            voided.setdefault(row["region"], set()).add(match.group(1))
    answer = {}
    for row in rows:
        if row["event"] != "verified":
            continue
        date = row["recorded_on"]
        if date in voided.get(row["region"], set()):
            continue
        if date not in signed.get(row["region"], set()):
            continue
        answer[row["region"]] = date
    return answer


def load_windows(order):
    answer = {}
    for name in order:
        path = None
        for candidate in os.listdir("history"):
            if candidate.endswith("-%s.md" % name):
                path = os.path.join("history", candidate)
                break
        if path is None:
            continue
        with open(path, encoding="utf-8") as fh:
            match = WINDOWS.search(fh.read())
        if match:
            base, declared, runtime = (int(part) for part in match.groups())
            answer[name] = {"declared": base + declared, "effective": base + runtime}
    return answer


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    order = [stage["name"] for stage in manifest["stages"]]
    rows = load()
    by_region = {}
    for row in rows:
        by_region.setdefault(row["region"], []).append(row)
    done = resolve(rows)
    windows = load_windows(order)
    rule = "=" * 76
    print("%s regional retention audit" % manifest["project"])
    print("source: %s" % LEDGER)
    print(rule)
    print("%d history records over %d regions, ordered by the manifest." % (len(rows), len(order)))
    print("A verification counts only when its date is countersigned and not voided.")
    print("The audit derives both retention windows from each region's history record.")
    for index, name in enumerate(order):
        print("")
        print("[%02d/%02d] %s" % (index + 1, len(order), name))
        for row in by_region.get(name, []):
            print("  %-12s %-14s %-16s %s" %
                  (row["recorded_on"], row["event"], row["actor"], row["detail"]))
        if name in done:
            print("  -> verified_on = %s   (countersigned)" % done[name])
        else:
            print("  -> verified_on = none   (no completed verification)")
        if name in windows:
            pair = windows[name]
            print("  -> windows: declared=%d effective=%d" %
                  (pair["declared"], pair["effective"]))
    print("")
    print(rule)
    print("%d of %d regions have completed verification." % (len(done), len(order)))


if __name__ == "__main__":
    main()
