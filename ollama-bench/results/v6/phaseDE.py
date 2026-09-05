"""v6 phases D and E.

D -- three trials on the best two survivors, both bands, at the top rung up to 64k. These are
the verdict rows. Ranking is plan section 6D: pass rate, then confidently-wrong rate, then
median wall. pibench resumes, so trial 0 is never re-run; only trials 1 and 2 are new work.

E -- the stretch. Each phase D quant that also placed at 96k or above runs the large band once
at that rung. Quality should not move; the point is a measured cell at the larger context, and
at 96k the working-margin rule admits all eight large-band tasks, which makes it the only place
g04 and t04 are scored at all (D6-1).

Run: python3 results/v6/phaseDE.py
"""
import json, os, statistics, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
RES = os.path.join(BENCH, "results")
sys.path.insert(0, HERE)
from phaseC import admits, CTXNAME, run_cell, runs_for   # noqa: E402


def rank(quant, ctx):
    runs = runs_for(quant, ctx, "large") + runs_for(quant, ctx, "tiny")
    if not runs:
        return None
    n = len(runs)
    return (-sum(x["pass"] for x in runs) / n,
            sum(1 for x in runs if x.get("verdict") == "confidently_wrong") / n,
            statistics.median(x["wall_s"] for x in runs))


def top_rung_any(quant):
    """Highest projector-free rung this quant placed pass or marginal at, no 64k cap."""
    best = None
    for r in json.load(open(os.path.join(HERE, "placement.json"), encoding="utf-8")):
        if r["quant"] != quant or r.get("has_projector"):
            continue
        if r.get("verdict") not in ("pass", "marginal"):
            continue
        if best is None or r["num_ctx"] > best["num_ctx"]:
            best = r
    return best


def main():
    b = json.load(open(os.path.join(HERE, "phaseB.json"), encoding="utf-8"))
    cands = [(r["quant"], r["num_ctx"]) for r in b["survivors_best_first"]]
    ref_ctx = max(x["num_ctx"] for x in b["reference"])
    cands = [("Q2_K_L", ref_ctx)] + cands
    scored = [(rank(q, c), q, c) for q, c in cands]
    scored = [s for s in scored if s[0] is not None]
    scored.sort(key=lambda s: s[0])
    best2 = scored[:2]
    print("== phase D ranking (pass rate, then cw rate, then median wall):", flush=True)
    for k, q, c in scored:
        print("   %-10s %-5s pass %.0f%%  cw %.0f%%  median wall %.0fs"
              % (q, CTXNAME[c], -k[0] * 100, k[1] * 100, k[2]), flush=True)
    print("== phase D takes:", [(q, CTXNAME[c]) for _, q, c in best2], flush=True)

    for _, q, c in best2:
        print("== phase D: %s at %s, three trials, both bands" % (q, CTXNAME[c]), flush=True)
        for t in admits(c):
            run_cell(q, c, "large", t, 3)
        run_cell(q, c, "tiny", "g01,g02,g03,g04,t01,t02,t03,t04", 3)
    open(os.path.join(HERE, ".phaseD-done"), "w").write("")

    # E -- stretch, only for a phase D quant that placed at 96k or above.
    stretched = []
    for _, q, c in best2:
        top = top_rung_any(q)
        if top and top["num_ctx"] >= 98304:
            sc = top["num_ctx"]
            print("== phase E: %s at %s, large band once (all eight tasks admitted)"
                  % (q, CTXNAME[sc]), flush=True)
            for t in admits(sc):
                run_cell(q, sc, "large", t, 1)
            stretched.append({"quant": q, "num_ctx": sc})
        else:
            print("== phase E: %s placed no rung at 96k or above; nothing to stretch" % q,
                  flush=True)
    json.dump({"phase_d": [{"quant": q, "num_ctx": c} for _, q, c in best2],
               "phase_e": stretched, "written": time.strftime("%Y-%m-%d %H:%M:%S")},
              open(os.path.join(HERE, "phaseDE.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(HERE, ".phaseE-done"), "w").write("")
    print("== phases D and E complete", flush=True)


if __name__ == "__main__":
    sys.exit(main())
