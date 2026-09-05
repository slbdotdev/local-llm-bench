"""Record each scored task's band and its MEASURED material size, per plan section 3.2.

Two bands hold the same eight task families (decisions.md, 2026-09-05):

  small  the family at its natural size, run at 24k -- `round2/suite-<trial>/`
  large  the same question over 30k-45k tokens,  run at 64k -- `round3/suite/`

Sizes are measured here, not copied from any worker's MANIFEST.json. The constant is 4.664
characters per token, measured for this suite; 5.95 was 28% wrong and would silently overflow
a window.

  python3 make_band_manifest.py            writes bands-2026-09-05.json and prints the table
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measure_material import measure, band, CPT  # noqa: E402

SMALL = os.path.join(HERE, "round2")
LARGE = os.path.join(HERE, "round3", "suite")
TRIALS = (0, 1, 2)


def size_of(task_dir):
    chars, nfiles = measure(os.path.join(task_dir, "seed"))
    return {"material_chars": chars, "material_tokens": round(chars / CPT),
            "seed_files": nfiles, "band": band(round(chars / CPT))}


def main():
    out = {"chars_per_token": CPT, "bands": {}}
    tasks = sorted(os.listdir(os.path.join(SMALL, "suite-0")))
    rows = []
    for t in tasks:
        # the small band rotates two tasks, so record every variant it actually runs
        per_trial = {}
        for tr in TRIALS:
            m = json.load(open(os.path.join(SMALL, f"mapping-{tr}.json")))
            d = os.path.join(SMALL, f"suite-{tr}", t)
            per_trial[f"trial-{tr}"] = dict(candidate=m[t], **size_of(d))
        toks = [v["material_tokens"] for v in per_trial.values()]
        large = None
        ld = os.path.join(LARGE, t)
        if os.path.isdir(ld):
            lm = json.load(open(os.path.join(HERE, "round3", "mapping.json")))
            large = dict(candidate=lm.get(t), **size_of(ld))
        out["bands"][t] = {"small": per_trial, "large": large}
        rows.append((t, per_trial["trial-0"]["candidate"], min(toks), max(toks),
                     (large or {}).get("candidate"), (large or {}).get("material_tokens")))

    print(f"{'task':6s}{'small candidate':22s}{'small tokens':>14s}   "
          f"{'large candidate':18s}{'large tokens':>13s}")
    for t, sc, lo, hi, lc, lt in rows:
        span = f"{lo}" if lo == hi else f"{lo}-{hi}"
        print(f"{t:6s}{sc or '-':22s}{span:>14s}   {lc or 'NOT AUTHORED':18s}"
              f"{(str(lt) if lt else '-'):>13s}")
    p = os.path.join(HERE, "bands-2026-09-05.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("\nwrote", p)


if __name__ == "__main__":
    main()
