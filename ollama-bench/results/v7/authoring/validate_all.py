#!/usr/bin/env python3
"""One command that says whether every v7 candidate is sound, and names what is not.

    python3 validate_all.py [--family luna] [--slot m05-main-luna] [--json report.json]

Six checks per candidate, in the order that a failure is cheapest to diagnose:

  files       the six files AUTHORING-BRIEF.md section 3 requires all exist
  band        measured material is inside the band MANIFEST.json declares
  clean       no __pycache__, .pytest_cache or *.pyc under seed/
  compiles    every .py under seed/ compiles
  selfcheck   selfcheck.py exits 0 — the reference satisfies the prompt's own examples
  probe       probe_candidate.py: reference passes, untouched sandbox is a clean
              visibly_failed, and no whitespace perturbation of a correct answer changes the
              verdict, EXCEPT where the candidate's NOTES.md adjudicates it

The last exception is deliberate and is why the probe's own exit code is not enough on its own.
Some prompts state their output format exactly — a first line that must be one of two strings, a
CSV whose separator, ordering and line endings are all specified — and for those a perturbation
SHOULD fail. This script reads the adjudication out of NOTES.md rather than guessing, so an
honest strictness and an accidental one are told apart by what the author wrote down.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHARS_PER_TOKEN = 4.664
BANDS = {"main": (29000, 36000), "cheap": (4000, 7000)}
REQUIRED = ["prompt.md", "test.py", "seed", "ref", "NOTES.md", "MANIFEST.json", "selfcheck.py"]
JUNK = ("__pycache__", ".pytest_cache")


def candidates(family=None, slot=None):
    out = []
    for fam in sorted(d for d in os.listdir(HERE) if d.startswith("cand-")):
        if family and fam != "cand-" + family:
            continue
        base = os.path.join(HERE, fam)
        for name in sorted(os.listdir(base)):
            if slot and name != slot:
                continue
            if os.path.isdir(os.path.join(base, name, "seed")):
                out.append(os.path.join(base, name))
    return out


def measure(seed):
    chars = files = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in JUNK + (".git",)]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            try:
                with open(os.path.join(base, n), encoding="utf-8") as fh:
                    chars += len(fh.read())
            except UnicodeDecodeError:
                with open(os.path.join(base, n), "rb") as fh:
                    chars += len(fh.read())
            files += 1
    return files, chars


def junk(seed):
    hits = []
    for base, dirs, names in os.walk(seed):
        for d in dirs:
            if d in JUNK:
                hits.append(os.path.relpath(os.path.join(base, d), seed))
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                hits.append(os.path.relpath(os.path.join(base, n), seed))
    return hits


def adjudicated(cand):
    """Perturbations the candidate's NOTES.md says are meant to fail."""
    notes = os.path.join(cand, "NOTES.md")
    if not os.path.exists(notes):
        return set()
    text = open(notes, encoding="utf-8").read().lower()
    out = set()
    for key, words in (("no_trailing_newline", ("final newline", "trailing newline")),
                       ("extra_trailing_nl", ("extra newline", "two trailing newlines",
                                              "extra blank line", "extra trailing newline")),
                       ("crlf", ("crlf", "lf line ending", "line endings")),
                       ("leading_blank", ("leading blank", "first line")),
                       ("trailing_spaces", ("trailing space", "trailing whitespace",
                                            "no spaces"))):
        if any(w in text for w in words) and ("must fail" in text or "adjudicat" in text
                                              or "stated" in text or "legitimate" in text):
            out.add("perturb:" + key)
    return out


def run(cand):
    slot = os.path.basename(cand)
    rec = {"slot": slot, "family": os.path.basename(os.path.dirname(cand))[5:], "problems": []}

    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(cand, f))]
    rec["files"] = "ok" if not missing else "missing " + ", ".join(missing)
    if missing:
        rec["problems"].append("missing required file(s): " + ", ".join(missing))

    mp = os.path.join(cand, "MANIFEST.json")
    band = None
    if os.path.exists(mp):
        try:
            band = json.load(open(mp, encoding="utf-8")).get("band")
        except Exception:
            rec["problems"].append("MANIFEST.json is not valid JSON")
    band = band or ("main" if "-main-" in slot else "cheap")
    files, chars = measure(os.path.join(cand, "seed"))
    tokens = int(round(chars / CHARS_PER_TOKEN))
    rec.update({"band": band, "tokens": tokens, "seed_files": files})
    lo, hi = BANDS[band]
    rec["band_ok"] = lo <= tokens <= hi
    if not rec["band_ok"]:
        rec["problems"].append("%d tokens is outside the %s band (%d-%d)" % (tokens, band, lo, hi))

    j = junk(os.path.join(cand, "seed"))
    rec["clean"] = not j
    if j:
        rec["problems"].append("build artifacts in seed/: " + ", ".join(sorted(set(j))[:4]))

    # -b writes the .pyc beside the source instead of into __pycache__, and the sweep below
    # removes them: a validator that leaves build artifacts in the material is the very
    # defect this script exists to report (D7-8).
    c = subprocess.run([sys.executable, "-m", "compileall", "-q", "-b",
                        os.path.join(cand, "seed")], capture_output=True, text=True)
    rec["compiles"] = c.returncode == 0
    for base, dirs, names in os.walk(os.path.join(cand, "seed")):
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                os.remove(os.path.join(base, n))
    if c.returncode != 0:
        rec["problems"].append("seed does not compile: " + c.stdout.strip()[-160:])

    sc = os.path.join(cand, "selfcheck.py")
    if os.path.exists(sc):
        # PYTHONDONTWRITEBYTECODE is the fix for a defect this script kept re-creating: a
        # selfcheck imports the seed's modules, CPython writes __pycache__ beside them, and the
        # next run of this very script reports "build artifacts in seed/". Sweeping afterwards
        # treats the symptom; not writing them treats the cause (D7-23).
        s = subprocess.run([sys.executable, "selfcheck.py"], cwd=cand, capture_output=True,
                           text=True, timeout=600,
                           env=dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"))
        rec["selfcheck"] = s.returncode == 0
        if s.returncode != 0:
            rec["problems"].append("selfcheck: " + (s.stdout or s.stderr).strip()[-200:])
    else:
        rec["selfcheck"] = False

    p = subprocess.run([sys.executable, os.path.join(HERE, "probe_candidate.py"), cand],
                       capture_output=True, text=True, timeout=1200)
    ok_ref = re.search(r"^reference\s+(\S+)\s+correct\s+0", p.stdout, re.M)
    ok_empty = re.search(r"^empty\s+\S+\s+visibly_failed", p.stdout, re.M)
    rec["reference"] = bool(ok_ref)
    rec["empty"] = bool(ok_empty) and "TRACEBACK" not in p.stdout
    if not ok_ref:
        rec["problems"].append("the reference solution does not pass its own grader")
    if not rec["empty"]:
        rec["problems"].append("an untouched sandbox is not a clean visibly_failed")
    adj = adjudicated(cand)
    unexplained = []
    for line in p.stdout.splitlines():
        m = re.search(r"GRADER DEFECT: (perturb:\w+)", line)
        if m and m.group(1) not in adj:
            unexplained.append(m.group(1))
    rec["perturbations"] = ("clean" if not unexplained
                            else "unexplained: " + ", ".join(unexplained))
    if unexplained:
        rec["problems"].append(
            "perturbation(s) fail a correct answer and NOTES.md does not adjudicate them: "
            + ", ".join(unexplained))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family")
    ap.add_argument("--slot")
    ap.add_argument("--json")
    a = ap.parse_args()

    rows = [run(c) for c in candidates(a.family, a.slot)]
    print("%-20s %-7s %-6s %-8s %-6s %-6s %-6s %-6s %s"
          % ("slot", "family", "band", "tokens", "files", "compil", "self", "ref", "state"))
    for r in rows:
        print("%-20s %-7s %-6s %-8d %-6s %-6s %-6s %-6s %s"
              % (r["slot"], r["family"], r["band"], r["tokens"],
                 "ok" if r["files"] == "ok" else "MISS",
                 "ok" if r["compiles"] else "FAIL",
                 "ok" if r.get("selfcheck") else "FAIL",
                 "ok" if r["reference"] else "FAIL",
                 "OK" if not r["problems"] else "%d problem(s)" % len(r["problems"])))
    bad = [r for r in rows if r["problems"]]
    if bad:
        print("\nPROBLEMS")
        for r in bad:
            print("  %s" % r["slot"])
            for p in r["problems"]:
                print("    - " + p)
    print("\n%d candidate(s), %d sound, %d with problems"
          % (len(rows), len(rows) - len(bad), len(bad)))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
