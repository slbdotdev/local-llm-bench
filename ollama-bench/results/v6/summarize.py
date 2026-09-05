"""Build the plan section 5 per-quant summary table from the v6 scored artifacts.

Reads every results/v6-<quant>-<ctx>-<band>.json plus results/v6/placement.json and writes
results/v6/summary.md. Verdict rule: v5 plan-rev5-focused section 7 as amended by v6 section 7
-- task-level, a task is solved when a majority of its trials pass under the section 4 timeout;
a class is viable when its quant solves three quarters of the class's tasks in that cell
(rounded up) and marginal at half. The confidently-wrong rate is a verdict line of its own and
outranks pass rate.
"""
import glob, json, math, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate import verdict_of
RES = os.path.dirname(HERE)

def med(xs):
    return statistics.median(xs) if xs else None

place = []
p = os.path.join(HERE, "placement.json")
if os.path.exists(p):
    place = json.load(open(p, encoding="utf-8"))
    for _r in place:                  # re-derive (D6-19)
        _r["verdict"], _r["verdict_why"] = verdict_of(_r)

def latest_per_cell(records):
    """A cell measured twice is superseded by its later record -- the projector-free rebake
    supersedes the projector build (D6-9/D6-11), and any re-measurement supersedes the run it
    repeats. Keyed on (quant, num_ctx), last write wins."""
    seen = {}
    for r in records:
        seen[(r["quant"], r["num_ctx"])] = r
    return list(seen.values())


def placement_for(quant):
    rs = [r for r in latest_per_cell(place) if r["quant"] == quant]
    ok = [r for r in rs if r.get("verdict") in ("pass", "marginal")]
    best = max(ok, key=lambda r: r["num_ctx"]) if ok else None
    at64 = next((r for r in rs if r["num_ctx"] == 65536), None)
    return best, at64

cells = {}   # (quant, ctxname, band) -> runs
for f in sorted(glob.glob(os.path.join(RES, "v6-*.json"))):
    base = os.path.basename(f)[:-5]
    if "hookproof" in base:
        continue
    parts = base.split("-")
    if len(parts) < 4:
        continue
    band, ctxname, quant = parts[-1], parts[-2], "-".join(parts[1:-2])
    d = json.load(open(f, encoding="utf-8"))
    runs = []
    for model, r in d.items():
        runs += r.get("runs", [])
    if runs:
        cells[(quant, ctxname, band)] = runs

def class_of(task):
    return "transform" if task.startswith("t") else "generate"

def verdict_words(runs):
    """Per-class viable/marginal/not viable under the arity rule."""
    by_task = {}
    for x in runs:
        by_task.setdefault(x["task"], []).append(bool(x["pass"]) and not x["timed_out"])
    out = {}
    for cls in ("generate", "transform"):
        ts = {t: v for t, v in by_task.items() if class_of(t) == cls}
        if not ts:
            continue
        n = len(ts)
        solved = sum(1 for v in ts.values() if sum(v) * 2 > len(v) or (len(v) == 1 and v[0]))
        need_viable, need_marg = math.ceil(0.75 * n), math.ceil(0.5 * n)
        w = "viable" if solved >= need_viable else ("marginal" if solved >= need_marg else "not viable")
        out[cls] = "%s (%d/%d solved)" % (w, solved, n)
    return out

rows = ["# v6 — per-quant summary (plan section 5)", "",
        "*Built by `summarize.py` from the scored artifacts and `placement.json`. Resident GB is",
        "`/api/ps` size / 2^30. `n` is trials, over the tasks the working-margin rule admits to the",
        "cell (D6-1), which is 8 in the tiny band, 6 in a 64k large band and 3 in a 48k one. Wall",
        "figures are seconds. `cw` is the confidently-wrong rate, which outranks pass rate.*", ""]

quants = sorted({k[0] for k in cells} | {r["quant"] for r in place})
rows += ["| quant | max viable ctx | resident | gen tok/s there | gen tok/s @64k |",
         "|---|---:|---:|---:|---:|"]
for q in quants:
    best, at64 = placement_for(q)
    rows.append("| %s | %s | %s | %s | %s |" % (
        q,
        "%dk" % (best["num_ctx"] // 1024) if best else "**none**",
        "%.2f GB" % best["resident_gb"] if best and best.get("resident_gb") else "-",
        "%.1f" % best["gen_tps_fill"] if best and best.get("gen_tps_fill") else "-",
        "%.1f" % at64["gen_tps_fill"] if at64 and at64.get("gen_tps_fill") else "-"))

rows += ["", "## Scored cells", "",
         "| cell | band | tasks | n | pass | cw rate | median wall | max wall | mean in tok | mean peak-prompt | mean out tok | turns | tools | timeouts | achieved out tok/s | generate | transform |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"]
for (q, cx, band), runs in sorted(cells.items()):
    n = len(runs)
    ntasks = len({x["task"] for x in runs})
    walls = [x["wall_s"] for x in runs]
    cw = sum(1 for x in runs if x.get("verdict") == "confidently_wrong")
    ach = [x["out_tokens"] / x["wall_s"] for x in runs if x["wall_s"] > 0]
    vw = verdict_words(runs)
    rows.append("| %s-%s | %s | %d | %d | %d/%d | %.0f%% | %.0f | %.0f | %.0f | %.0f | %.0f | %.1f | %.1f | %d | %.1f | %s | %s |" % (
        q, cx, band, ntasks, n,
        sum(x["pass"] for x in runs), n, 100.0 * cw / n,
        med(walls), max(walls),
        statistics.mean(x["in_tokens"] for x in runs),
        statistics.mean(x.get("achieved_fill_prompt_tokens", 0) for x in runs),
        statistics.mean(x["out_tokens"] for x in runs),
        statistics.mean(x["turns"] for x in runs),
        statistics.mean(x["tool_calls"] for x in runs),
        sum(1 for x in runs if x["timed_out"]),
        statistics.mean(ach) if ach else 0.0,
        vw.get("generate", "-"), vw.get("transform", "-")))

rows += ["", "## Per task (passes/trials)", ""]
tasks = sorted({x["task"] for runs in cells.values() for x in runs})
hdr = sorted(cells)
rows.append("| task | " + " | ".join("%s-%s %s" % k for k in hdr) + " |")
rows.append("|---|" + "---|" * len(hdr))
for t in tasks:
    cs = []
    for k in hdr:
        rs = [x for x in cells[k] if x["task"] == t]
        cs.append("%d/%d" % (sum(x["pass"] for x in rs), len(rs)) if rs else "-")
    rows.append("| %s | %s |" % (t, " | ".join(cs)))

open(os.path.join(HERE, "summary.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("\n".join(rows))
