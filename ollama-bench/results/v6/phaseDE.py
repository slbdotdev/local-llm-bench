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
RES = os.path.dirname(HERE)              # .../ollama-bench/results -- where the tag JSONs live
BENCH = os.path.dirname(RES)             # .../ollama-bench -- where pibench.py lives
sys.path.insert(0, HERE)
from phaseC import admits, CTXNAME, run_cell, runs_for   # noqa: E402
from gate import verdict_of                              # noqa: E402


# The owner's just-in-time pull rule (D6-29): the deferred UD-IQ3_S download starts only when
# the GPU is already inside the campaign's final scored cell, so it overlaps exactly one trial.
# If there is no room left afterwards for the placement, it does not start at all.
JIT_NAME = "UDIQ3S"
JIT_SRC = "hf.co/unsloth/Qwen3.8-27B-GGUF:UD-IQ3_S"
JIT_CUTOFF = "05:45"        # local clock; past this the night belongs to the handoff


def maybe_jit_pull():
    now = time.strftime("%H:%M")
    if now >= JIT_CUTOFF:
        print("== JIT pull SKIPPED: %s is past the %s cutoff, no room for the placement "
              "(D6-29); UD-IQ3_S stays a -partial on disk for the next session"
              % (now, JIT_CUTOFF), flush=True)
        return
    print("== JIT pull: launching the UD-IQ3_S resume alongside the final scored cell "
          "(D6-29)", flush=True)
    subprocess.Popen(["setsid", "nohup", "bash", os.path.join(HERE, "jit_pull.sh"),
                      JIT_NAME, JIT_SRC],
                     cwd=BENCH, stdout=open(os.path.join(HERE, "jitpull.log"), "w"),
                     stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                     start_new_session=True)


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
        v, _ = verdict_of(r)              # re-derive; the stored verdict may predate a rule (D6-35)
        if v != "pass":                   # a stretch cell must be clean, never marginal (D6-33)
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
    # An empty selection means no scored artifact could be read, and phases D and E would
    # "complete" with zero verdict rows while every flag said success (D6-31).
    if not best2:
        raise SystemExit("FATAL: phase D selected no quant -- no scored rows were readable "
                         "from %s. Refusing to report an empty campaign as complete." % RES)
    print("== phase D ranking (pass rate, then cw rate, then median wall):", flush=True)
    for k, q, c in scored:
        print("   %-10s %-5s pass %.0f%%  cw %.0f%%  median wall %.0fs"
              % (q, CTXNAME[c], -k[0] * 100, k[1] * 100, k[2]), flush=True)
    print("== phase D takes:", [(q, CTXNAME[c]) for _, q, c in best2], flush=True)

    # Build every remaining scored cell up front, so the LAST one is knowable before it starts.
    # The owner's just-in-time pull rule (D6-29) launches the deferred download at the start of
    # that final cell and nowhere earlier.
    cells = []
    for _, q, c in best2:
        for t in admits(c):
            cells.append(("D", q, c, "large", t, 3))
        cells.append(("D", q, c, "tiny", "g01,g02,g03,g04,t01,t02,t03,t04", 3))
    stretched = []
    for _, q, c in best2:
        top = top_rung_any(q)
        if top and top["num_ctx"] >= 98304:
            sc = top["num_ctx"]
            for t in admits(sc):
                cells.append(("E", q, sc, "large", t, 1))
            stretched.append({"quant": q, "num_ctx": sc})
        else:
            print("== phase E: %s placed no rung at 96k or above; nothing to stretch" % q,
                  flush=True)

    d_done = False
    for i, (kind, q, c, band, tasks, trials) in enumerate(cells):
        if kind == "E" and not d_done:
            open(os.path.join(HERE, ".phaseD-done"), "w").write("")
            d_done = True
        if i == len(cells) - 1:
            maybe_jit_pull()
        print("== phase %s: %s at %s, %s band, %s, %d trial(s)"
              % (kind, q, CTXNAME[c], band, tasks, trials), flush=True)
        run_cell(q, c, band, tasks, trials)
    if not d_done:
        open(os.path.join(HERE, ".phaseD-done"), "w").write("")

    json.dump({"phase_d": [{"quant": q, "num_ctx": c} for _, q, c in best2],
               "phase_e": stretched, "cells_run": len(cells),
               "written": time.strftime("%Y-%m-%d %H:%M:%S")},
              open(os.path.join(HERE, "phaseDE.json"), "w", encoding="utf-8"), indent=1)
    # .phaseE-done is load-bearing twice over: the session waiter treats it as the end of the
    # campaign, and jit_pull.sh waits on it before touching the GPU (D6-29).
    open(os.path.join(HERE, ".phaseE-done"), "w").write("")
    print("== phases D and E complete", flush=True)


if __name__ == "__main__":
    sys.exit(main())
