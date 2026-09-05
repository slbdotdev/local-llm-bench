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
RES = os.path.dirname(HERE)              # .../ollama-bench/results -- where the tag JSONs live
BENCH = os.path.dirname(RES)             # .../ollama-bench -- where pibench.py lives
CTXNAME = {49152: "48k", 65536: "64k", 98304: "96k", 131072: "128k",
           196608: "192k", 262144: "256k"}


def placement():
    return json.load(open(os.path.join(HERE, "placement.json"), encoding="utf-8"))


def rungs(quant, cap=65536):
    """Every projector-free rung <= cap that placed pass or marginal, highest first.

    A quant is tried at its highest rung and DEMOTED one rung on a sentinel failure, not
    rejected outright (D6-17) -- a marginal cell failing the sentinel says the cell is too
    slow, which is what marginal already meant; it does not say the quant is bad. Rejection is
    for a quant that fails the sentinel at every rung it placed on.
    """
    seen = {}
    for r in placement():
        if r["quant"] != quant or r["num_ctx"] > cap:
            continue
        if r.get("has_projector"):          # superseded build (D6-9/D6-11)
            continue
        if r.get("verdict") not in ("pass", "marginal"):
            continue
        seen[r["num_ctx"]] = r              # later record wins
    return [seen[c] for c in sorted(seen, reverse=True)]


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
    # A None here means the artifacts could not be read, and the 3x rejection test would then
    # quietly never fire (D6-31). Fail loudly instead of measuring nothing.
    if not any(v is not None for v in ref.values()):
        raise SystemExit("FATAL: no reference t03 wall could be read from %s -- the 3x "
                         "rejection rule would be inert. Refusing to run phase B." % RES)

    # 2. Every other quant at its own top rung.
    placed, rejected, demoted = [], [], []
    for q in quants:
        if q == "Q2_K_L":
            continue
        cands = rungs(q)
        if not cands:
            rejected.append((q, None, "no rung placed under the line"))
            continue
        why_last = None
        for i, best in enumerate(cands):
            ctx = best["num_ctx"]
            print("== sentinels: %s at %s (%s)" % (q, CTXNAME[ctx], best.get("verdict")),
                  flush=True)
            run_cell(q, ctx, "large", "g03,t03", 1)
            w, n_to = wall(q, ctx, "t03"), timed_out_any(q, ctx)
            r = ref.get(ctx)
            if n_to:
                why_last = "timed out on %d of 2 sentinels at %s" % (n_to, CTXNAME[ctx])
            elif w is None:
                why_last = "no t03 result at %s" % CTXNAME[ctx]
            elif r and w > 3 * r:
                why_last = ("t03 %.0fs at %s is over 3x the reference %.0fs"
                            % (w, CTXNAME[ctx], r))
            else:
                placed.append((q, ctx, w))
                if i:
                    demoted.append({"quant": q, "from": CTXNAME[cands[0]["num_ctx"]],
                                    "to": CTXNAME[ctx], "why": why_last})
                why_last = None
                break
            print("   %s -- demoting a rung" % why_last, flush=True)
        if why_last is not None:
            rejected.append((q, cands[-1]["num_ctx"],
                             "%s, and every lower placed rung too" % why_last))

    placed.sort(key=lambda x: x[2])
    order = [{"quant": q, "num_ctx": c, "t03_wall_s": w} for q, c, w in placed]
    ref_row = [{"quant": "Q2_K_L", "num_ctx": c, "t03_wall_s": ref[c]}
               for c in (65536, 49152) if ref.get(c)]
    out = {"reference": ref_row, "survivors_best_first": order, "demoted": demoted,
           "rejected": [{"quant": q, "num_ctx": c, "why": why} for q, c, why in rejected],
           "written": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(out, open(os.path.join(HERE, "phaseB.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1), flush=True)
    open(os.path.join(HERE, ".phaseB-done"), "w").write("")


if __name__ == "__main__":
    sys.exit(main())
