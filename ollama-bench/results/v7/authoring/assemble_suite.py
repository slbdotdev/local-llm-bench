#!/usr/bin/env python3
"""Assemble the accepted v7 suite from the three families' candidate directories.

    python3 assemble_suite.py [--check-only]

Reads `roundtable.md` for the accepted set — a line of the form

    | m05-main-luna | luna | claude: ACCEPT | glm: ACCEPT | accepted |

— copies each accepted candidate into `suite/<slot>/`, and then enforces the two structural
rules the plan sets, refusing to write an invalid suite rather than reporting one:

  * every failure mode 1-10 is covered at least twice, once per band;
  * no family authors more than 40% of the accepted tasks.

It also re-measures every task's band and re-runs `probe_candidate.py`'s two non-negotiable
rows (reference passes, untouched sandbox is visibly_failed and does not traceback), because a
candidate can be accepted on a review and still have drifted since.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.join(HERE, "suite")
ROUNDTABLE = os.path.join(HERE, "roundtable.md")
BANDS = {"main": (29000, 36000), "cheap": (4000, 7000), "cheap24": (12000, 16000)}
# `cheap24` is round three's wider cheap band, run at 24k. For the mode-coverage rule it
# counts as the cheap band: a mode still needs one task per band and never two of one.
BAND_CLASS = {"main": "main", "cheap": "cheap", "cheap24": "cheap"}
CAP = 0.40


def accepted():
    """Slots marked accepted in roundtable.md, in file order."""
    if not os.path.exists(ROUNDTABLE):
        print("roundtable.md not found; nothing to assemble", file=sys.stderr)
        return []
    # Only the register section counts. The narrative rounds below it also carry tables whose
    # cells name slots, and reading the whole file picked four of them up as extra acceptances
    # and then tried to copy a slot twice. The register is the record; prose about the register
    # is not.
    out = []
    seen = set()
    in_register = False
    for line in open(ROUNDTABLE, encoding="utf-8"):
        if line.startswith("## "):
            in_register = line.strip().lower().startswith("## the register")
            continue
        if not in_register or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        slot, family = cells[0], cells[1]
        # Rounds two, three and four name their slots m.., n.. and p..; the register holds
        # whichever generation is currently accepted for a mode and band.
        if cells[-1].lower().startswith("accepted") and re.match(r"^[a-z]\d\d-(main|cheap)-", slot):
            if slot in seen:
                raise SystemExit("roundtable.md lists %s in the register twice" % slot)
            seen.add(slot)
            out.append((slot, family))
    return out


def find(slot):
    for fam in sorted(d for d in os.listdir(HERE) if d.startswith("cand-")):
        p = os.path.join(HERE, fam, slot)
        if os.path.isdir(p):
            return p
    return None


def measure(seed):
    chars = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".pytest_cache")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            try:
                with open(os.path.join(base, n), encoding="utf-8") as fh:
                    chars += len(fh.read())
            except UnicodeDecodeError:
                with open(os.path.join(base, n), "rb") as fh:
                    chars += len(fh.read())
    return chars, int(round(chars / 4.664))


def probe(cand):
    r = subprocess.run([sys.executable, os.path.join(HERE, "probe_candidate.py"), cand],
                       capture_output=True, text=True, timeout=900)
    ref_ok = re.search(r"^reference\s+\S+\s+correct\s+0", r.stdout, re.M) is not None
    empty_ok = re.search(r"^empty\s+\S+\s+visibly_failed", r.stdout, re.M) is not None
    tb = "TRACEBACK" in r.stdout
    return ref_ok, empty_ok and not tb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    rows = accepted()
    if not rows:
        return 1
    problems = []
    modes = {}
    families = {}
    report = []

    for slot, family in rows:
        cand = find(slot)
        if cand is None:
            problems.append("%s: accepted but no candidate directory found" % slot)
            continue
        mpath = os.path.join(cand, "MANIFEST.json")
        man = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}
        band = man.get("band") or ("main" if "-main-" in slot else "cheap")
        mode = man.get("failure_mode") or int(slot[1:3])
        if band not in BANDS:
            problems.append("%s: unknown band %r" % (slot, band))
            continue
        chars, tokens = measure(os.path.join(cand, "seed"))
        lo, hi = BANDS[band]
        if not (lo <= tokens <= hi):
            problems.append("%s: %d tokens, outside the %s band (%d-%d)"
                            % (slot, tokens, band, lo, hi))
        ref_ok, empty_ok = probe(cand)
        if not ref_ok:
            problems.append("%s: reference solution does not pass its own grader" % slot)
        if not empty_ok:
            problems.append("%s: untouched sandbox is not a clean visibly_failed" % slot)
        modes.setdefault(mode, []).append(BAND_CLASS.get(band, band))
        families[family] = families.get(family, 0) + 1
        report.append((slot, family, band, mode, tokens, ref_ok, empty_ok))

    for mode in range(1, 11):
        bands = modes.get(mode, [])
        if len(bands) < 2:
            problems.append("failure mode %d is covered %d time(s); the plan requires two"
                            % (mode, len(bands)))
        elif set(bands) != {"main", "cheap"}:
            problems.append("failure mode %d is covered %r; the plan requires one of each band"
                            % (mode, bands))

    total = len(report)
    for fam, n in sorted(families.items()):
        if total and n / total > CAP:
            problems.append("%s authored %d of %d accepted tasks (%.0f%%), over the 40%% cap"
                            % (fam, n, total, 100.0 * n / total))

    print("%-20s %-8s %-6s %-5s %-8s %s" % ("slot", "family", "band", "mode", "tokens", "probe"))
    for slot, fam, band, mode, tokens, ref_ok, empty_ok in report:
        print("%-20s %-8s %-6s %-5d %-8d %s"
              % (slot, fam, band, mode, tokens,
                 "ok" if (ref_ok and empty_ok) else "FAILED"))
    print("\n%d accepted; by family %s" % (total, dict(sorted(families.items()))))

    if problems:
        print("\nNOT ASSEMBLED:")
        for p in problems:
            print("  - " + p)
        return 1
    if a.check_only:
        print("\nchecks pass; --check-only, so nothing was written")
        return 0

    if os.path.isdir(SUITE):
        shutil.rmtree(SUITE)
    os.makedirs(SUITE)
    for slot, fam, band, mode, tokens, _r, _e in report:
        shutil.copytree(find(slot), os.path.join(SUITE, slot))
    print("\nwrote %d tasks to %s" % (total, SUITE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
