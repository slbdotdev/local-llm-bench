"""Rapid quant smoke report: per quant x task on the fixed harness vs the reference ladder (fp8, Sonnet, Luna, Haiku).
Usage: python results/v5-smoke-report.py  -> prints markdown; reads results/v5-smoke-*.json and the reference files."""
import glob, json, os, statistics
TASKS = ["52_reengine", "55_minilang", "57_stateful", "60_numlit"]
def per_task_from_grades(p):
    g = json.load(open(p, encoding="utf-8")); out = {}
    for v in g.values(): out.setdefault(v["task"], []).append(v)
    return {t: (sum(x["pass"] for x in v), len(v), statistics.mean(x["score"] for x in v)) for t, v in out.items()}
def per_task_from_pibench(p):
    d = json.load(open(p, encoding="utf-8")); out = {}
    for r in d.values():
        for t in r.get("runs", []): out.setdefault(t["task"], []).append(t)
    return {t: (sum(1 for x in v if x.get("pass") and not x.get("timed_out")), len(v),
                statistics.mean((x.get("score") or 0.0) for x in v),
                sum(1 for x in v if x.get("timed_out")), statistics.mean(x.get("wall_s", 0) for x in v),
                statistics.mean(x.get("out_tokens", 0) for x in v)) for t, v in out.items()}
cols = {}
for f in sorted(glob.glob("results/v5-smoke-q27-*.json")) + sorted(glob.glob("results/v5-smoke-low-q27-*.json")):
    name = os.path.basename(f)[len("v5-smoke-"):-5]
    cols[name] = per_task_from_pibench(f)
ref = {"fp8 medium": per_task_from_pibench("results/v4-ref-medium-1800.json"),
       "Sonnet": per_task_from_grades("results/sonnet-v4/grades.json"),
       "Luna med": per_task_from_grades("results/codex-luna-v4/grades.json"),
       "Haiku": per_task_from_grades("results/haiku-v4/grades.json")}
names = list(cols) + list(ref)
print("| task | " + " | ".join(names) + " |"); print("|---|" + "---|" * len(names))
for t in TASKS:
    cells = []
    for n in names:
        v = (cols.get(n) or ref.get(n)).get(t)
        if not v: cells.append("-"); continue
        s = f"{v[0]}/{v[1]} ({v[2]:.2f})"
        if len(v) > 3 and v[3]: s += f" TO{v[3]}"
        cells.append(s)
    print(f"| {t} | " + " | ".join(cells) + " |")
print()
for n in names:
    src = cols.get(n) or ref.get(n); ts = [t for t in TASKS if t in src]
    if ts: print(f"- {n}: mean SCORE {statistics.mean(src[t][2] for t in ts):.3f} over {len(ts)} tasks, passes {sum(src[t][0] for t in ts)}/{sum(src[t][1] for t in ts)}"
                 + (f", mean out tokens {statistics.mean(src[t][5] for t in ts):.0f}, mean wall {statistics.mean(src[t][4] for t in ts):.0f} s" if len(src[ts[0]]) > 3 else ""))
print("\nCaveats: local runs use the fixed harness (results/pi-agent-v5: maxTokens 24576, compaction on) at 32k with a 1200 s")
print("timeout; a timed-out run keeps its partial score. Not comparable to the capped v4 local ranking. Reference rows are")
print("3 trials on their own harnesses (fp8 via OpenRouter/pi, Sonnet/Haiku via claude -p, Luna via codex-run medium).")
