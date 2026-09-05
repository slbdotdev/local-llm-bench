"""Measure each candidate's real seed-material size, in tokens, at the measured
4.664 chars/token constant, and assign the plan's band.

  python3 measure_material.py [--json out.json]

Band boundaries (plan-2026-09-05 section 3.2):
  small 4,000-8,000 | medium 12,000-20,000 | large 30,000-45,000
Anything below 4,000 is 'tiny' -- under the small band and not a scored band.
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "tasks-v5"))
CPT = 4.664
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_EXT = (".pyc", ".pyo")


def band(tok):
    if tok < 4000:
        return "tiny"
    if tok <= 8000:
        return "small"
    if tok < 12000:
        return "small-medium-gap"
    if tok <= 20000:
        return "medium"
    if tok < 30000:
        return "medium-large-gap"
    if tok <= 45000:
        return "large"
    return "oversize"


def measure(seed):
    chars = nfiles = 0
    for root, dirs, files in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(SKIP_EXT):
                continue
            p = os.path.join(root, f)
            try:
                chars += len(open(p, encoding="utf-8").read())
            except UnicodeDecodeError:
                chars += os.path.getsize(p)
            nfiles += 1
    return chars, nfiles


def main():
    rows = []
    for task in sorted(os.listdir(ROOT)):
        tdir = os.path.join(ROOT, task)
        if not os.path.isdir(tdir):
            continue
        for cand in sorted(os.listdir(tdir)):
            cdir = os.path.join(tdir, cand)
            if not os.path.isdir(cdir):
                continue
            seed = os.path.join(cdir, "seed")
            chars, nfiles = measure(seed) if os.path.isdir(seed) else (0, 0)
            promptp = os.path.join(cdir, "prompt.md")
            pchars = len(open(promptp, encoding="utf-8").read()) if os.path.isfile(promptp) else 0
            tok = round(chars / CPT)
            rows.append({"task": task, "cand": cand, "seed_files": nfiles,
                         "material_chars": chars, "material_tokens": tok,
                         "prompt_chars": pchars, "prompt_tokens": round(pchars / CPT),
                         "band": band(tok)})
    w = f"{'task':6s}{'cand':10s}{'files':>6s}{'chars':>9s}{'tokens':>8s}{'prompt_tok':>12s}  band"
    print(w)
    for r in rows:
        print(f"{r['task']:6s}{r['cand']:10s}{r['seed_files']:6d}{r['material_chars']:9d}"
              f"{r['material_tokens']:8d}{r['prompt_tokens']:12d}  {r['band']}")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(rows, open(out, "w", encoding="utf-8"), indent=1)
        print("\nwrote", out)


if __name__ == "__main__":
    main()
