"""v6 phase B -- sentinels (plan section 6B).

Two large-band tasks at each surviving quant's top rung up to 64k: t03 (the task that exposed
the bend) and g03 (the hardest; the only task Q2_K_L missed). One trial each. A quant is
rejected when it times out on either, or when its t03 wall is over 3x the reference quant's
t03 wall AT THE SAME RUNG -- so Q2_K_L runs the sentinels first, at both 48k and 64k, to give
a reference at each rung a candidate can place on.

Ordering for everything that follows is by t03 wall, best first, so a short night still leaves
the strongest candidates with complete rows.

Run: python3 results/v6/phaseB.py     (WSL python; it shells out to runcell.sh)
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
RES = os.path.join(BENCH, "results")
CTXNAME = {49152: "48k", 65536: "64k", 98304: "96k", 131072: "128k",
           196608: "192k", 262144: "256k"}


def placement():
    return json.load(open(os.path.join(HERE, "placement.json"), encoding="utf-8"))


def top_rung(quant, cap=65536):
    """Highest rung <= cap whose latest projector-free record placed pass or marginal."""
    best = None
    for r in placement():
        if r["quant"] != quant or r["num_ctx"] > cap:
            continue
        if r.get("has_projector"):          # superseded build (D6-9/D6-11)
            continue
        if r.get("verdict") not in ("pass", "marginal"):
            continue
        if best is None or r["num_ctx"] > best["num_ctx"]:
            best = r
    return best


def run_cell(quant, ctx, band, tasks, trials):
    cmd = ["bash", os.path.join(HERE, "runcell.sh"), quant, CTXNAME[ctx], str(ctx),
           band, tasks, str(trials)]
    print("  ->", " ".join(cmd[2:]), flush=True)
    return subprocess.run(cmd, cwd=BENCH).returncode


def runs_for(quant, ctx, band):
    f = os.path.join(RES, "v6-%s-%s-%s.json" % (quant, CTXNAME[ctx], band))
    if not os.path.exists(f):
        return []
    d = json.load(open(f, encoding="utf-8"))
    out = []
    for _, r in d.items():
        out += r.get("runs", [])
    return out


def wall(quant, ctx, task):
    rs = [x for x in runs_for(quant, ctx, "large") if x["task"] == task]
    return min((x["wall_s"] for x in rs), default=None)


def timed_out_any(quant, ctx):
    return sum(1 for x in runs_for(quant, ctx, "large") if x["timed_out"])


def main():
    quants = sorted({r["quant"] for r in placement()})
    # 1. Reference first, at both rungs a candidate can place on.
    print("== reference sentinels: Q2_K_L at 64k and 48k", flush=True)
    for ctx in (65536, 49152):
        run_cell("Q2_K_L", ctx, "large", "g03,t03", 1)
    ref = {ctx: wall("Q2_K_L", ctx, "t03") for ctx in (65536, 49152)}
    print("== reference t03 walls:", ref, flush=True)

    # 2. Every other quant at its own top rung.
    placed, rejected = [], []
    for q in quants:
        if q == "Q2_K_L":
            continue
        best = top_rung(q)
        if best is None:
            rejected.append((q, None, "no rung placed under the line"))
            continue
        ctx = best["num_ctx"]
        print("== sentinels: %s at %s" % (q, CTXNAME[ctx]), flush=True)
        run_cell(q, ctx, "large", "g03,t03", 1)
        w, n_to = wall(q, ctx, "t03"), timed_out_any(q, ctx)
        r = ref.get(ctx)
        if n_to:
            rejected.append((q, ctx, "timed out on %d of 2 sentinels" % n_to))
        elif w is None:
            rejected.append((q, ctx, "no t03 result"))
        elif r and w > 3 * r:
            rejected.append((q, ctx, "t03 %.0fs is over 3x the %s reference %.0fs"
                             % (w, CTXNAME[ctx], r)))
        else:
            placed.append((q, ctx, w))

    placed.sort(key=lambda x: x[2])
    order = [{"quant": q, "num_ctx": c, "t03_wall_s": w} for q, c, w in placed]
    ref_row = [{"quant": "Q2_K_L", "num_ctx": c, "t03_wall_s": ref[c]}
               for c in (65536, 49152) if ref.get(c)]
    out = {"reference": ref_row, "survivors_best_first": order,
           "rejected": [{"quant": q, "num_ctx": c, "why": why} for q, c, why in rejected],
           "written": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(out, open(os.path.join(HERE, "phaseB.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1), flush=True)
    open(os.path.join(HERE, ".phaseB-done"), "w").write("")


if __name__ == "__main__":
    sys.exit(main())
