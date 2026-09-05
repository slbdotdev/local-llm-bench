"""v6 phase C -- one trial, both bands, every survivor at its top rung up to 64k.

Order comes from phaseB.json (best first by t03 wall). Both bands run in the quant's own cell
(D6-7). The working-margin rule (D6-1) decides which large-band tasks the cell admits.

Two timeouts on a quant reject it mid-row (plan section 4), so the large band is driven one
task at a time -- six extra model loads a quant, about ninety seconds, against a worst case of
an hour spent finishing a cell that is already rejected. The tiny band runs as one cell: its
300 s timeout caps the whole band at forty minutes and nothing there has ever timed out.

Run: python3 results/v6/phaseC.py
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
RES = os.path.join(BENCH, "results")
CTXNAME = {49152: "48k", 65536: "64k", 98304: "96k", 131072: "128k",
           196608: "192k", 262144: "256k"}
# Large-band material in tokens, from authoring/bands-2026-09-05.json.
MATERIAL = {"g01": 30001, "g02": 32476, "g03": 30018, "g04": 42570,
            "t01": 36643, "t02": 31102, "t03": 30604, "t04": 41138}
TINY = "g01,g02,g03,g04,t01,t02,t03,t04"


def admits(ctx):
    """The working-margin rule (D6-1, D6-12): num_ctx >= 1.6x the task's material.

    v5 plan section 3.3 states the rule twice -- "at least 1.6x the material" and "the material
    must never exceed about 60% of the window" -- and the two disagree by a hair, since 1/1.6 is
    62.5%. Taken literally the 60% form admits nothing at all at 48k, while v6 plan section 6C
    says in as many words that a 48k-only quant runs "the three large-band tasks that fit". So
    the 1.6x form is the operative test and "about 60%" is its approximate restatement.
    """
    return [t for t, m in sorted(MATERIAL.items()) if ctx >= 1.6 * m]


def run_cell(quant, ctx, band, tasks, trials):
    cmd = ["bash", os.path.join(HERE, "runcell.sh"), quant, CTXNAME[ctx], str(ctx),
           band, tasks, str(trials)]
    print("  ->", " ".join(cmd[2:]), flush=True)
    return subprocess.run(cmd, cwd=BENCH).returncode


def runs_for(quant, ctx, band):
    f = os.path.join(RES, "v6-%s-%s-%s.json" % (quant, CTXNAME[ctx], band))
    if not os.path.exists(f):
        return []
    out = []
    for _, r in json.load(open(f, encoding="utf-8")).items():
        out += r.get("runs", [])
    return out


def n_timeouts(quant, ctx):
    return sum(1 for b in ("large", "tiny") for x in runs_for(quant, ctx, b) if x["timed_out"])


def main(trials=1):
    b = json.load(open(os.path.join(HERE, "phaseB.json"), encoding="utf-8"))
    order = [(r["quant"], r["num_ctx"]) for r in b["survivors_best_first"]]
    ref = [(r["quant"], r["num_ctx"]) for r in b["reference"]]
    # The reference quant runs first and at its best rung only.
    todo = [max(ref, key=lambda x: x[1])] + [x for x in order if x[0] != "Q2_K_L"]

    rejected = []
    for quant, ctx in todo:
        tasks = admits(ctx)
        print("== %s at %s: large band %s, tiny band all 8" % (quant, CTXNAME[ctx], tasks),
              flush=True)
        killed = False
        for t in tasks:                       # one task at a time, so a rejection lands early
            run_cell(quant, ctx, "large", t, trials)
            if n_timeouts(quant, ctx) >= 2:
                rejected.append((quant, ctx, "two timeouts, rejected mid-row at %s" % t))
                killed = True
                break
        if killed:
            continue
        run_cell(quant, ctx, "tiny", TINY, trials)
        if n_timeouts(quant, ctx) >= 2:
            rejected.append((quant, ctx, "two timeouts across the two bands"))

    out = {"rejected": [{"quant": q, "num_ctx": c, "why": w} for q, c, w in rejected],
           "written": time.strftime("%Y-%m-%d %H:%M:%S"), "trials": trials}
    json.dump(out, open(os.path.join(HERE, "phaseC.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1), flush=True)
    open(os.path.join(HERE, ".phaseC-done"), "w").write("")


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 1))
