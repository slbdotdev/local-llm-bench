#!/usr/bin/env python3
"""The suite composition table, generated from the suite on disk rather than from the plan.

    python3 composition.py [<suite-dir>]

The handoff has to say what the suite *is*, and a table typed by hand drifts from the directory
it describes within one revision — the same failure `stamp_notes.py` exists to prevent one level
down. So this reads every accepted task's MANIFEST.json and measures its material itself, at the
campaign's measured 4.664 characters per token, and prints the markdown table and the family and
mode coverage counts underneath it.
"""
import json
import os
import sys

CHARS_PER_TOKEN = 4.664
BANDS = {"main": (29000, 36000), "cheap": (4000, 7000)}
JUNK = ("__pycache__", ".pytest_cache", ".git")


def measure(seed):
    chars = files = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in JUNK]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(base, n)
            try:
                with open(p, encoding="utf-8") as fh:
                    chars += len(fh.read())
            except UnicodeDecodeError:
                with open(p, "rb") as fh:
                    chars += len(fh.read())
            files += 1
    return files, chars


def subchecks(cand):
    """How many independent subchecks the grader scores, read out of its own SCORE total."""
    mp = os.path.join(cand, "MANIFEST.json")
    if os.path.exists(mp):
        try:
            m = json.load(open(mp, encoding="utf-8"))
            for k in ("subchecks", "n_subchecks", "checks"):
                if isinstance(m.get(k), int):
                    return m[k]
        except Exception:
            pass
    return None


def main():
    suite = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "suite")
    slots = sorted(d for d in os.listdir(suite) if os.path.isdir(os.path.join(suite, d)))

    # The occupancy column is against each band's OWN window — 48k for main, 24k for cheap —
    # because that is the figure the calibration plan reads before it reads a pass rate. A main
    # figure and a cheap figure in one column against one denominator would be a category error.
    print("| slot | mode | band | author | seed files | material (tokens) | window | occupancy |")
    print("| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |")
    fam = {}
    mode = {}
    for s in slots:
        cand = os.path.join(suite, s)
        parts = s.split("-")
        m = parts[0].lstrip("m").lstrip("0") or "0"
        band = parts[1]
        author = parts[2] if len(parts) > 2 else "?"
        files, chars = measure(os.path.join(cand, "seed"))
        tok = int(round(chars / CHARS_PER_TOKEN))
        window = 48000 if band == "main" else 24000
        fam[author] = fam.get(author, 0) + 1
        mode.setdefault(int(m), []).append(s)
        flag = "" if BANDS[band][0] <= tok <= BANDS[band][1] else " **out of band**"
        print("| %s | %s | %s | %s | %d | %s%s | %dk | %.0f%% |"
              % (s, m, band, author, files, "{:,}".format(tok), flag,
                 window // 1000, 100.0 * tok / window))

    n = len(slots)
    print("\n**%d tasks.** Family share: %s."
          % (n, ", ".join("%s %d (%.0f%%)" % (k, v, 100.0 * v / n)
                          for k, v in sorted(fam.items()))))
    missing = [k for k in range(1, 11) if len(mode.get(k, [])) != 2]
    print("Mode coverage: %s."
          % ("all ten modes twice" if not missing
             else "INCOMPLETE — modes " + ", ".join(str(k) for k in missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
