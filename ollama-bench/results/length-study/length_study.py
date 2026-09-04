# Length-vs-outcome study on tasks-v4. Read-only: writes nothing outside results/length-study/.
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = ["52_reengine", "55_minilang", "56_tmpl", "57_stateful", "59_uri", "60_numlit", "61_codecs"]

# clause counting rule: a "requirement clause" is a top-level markdown list item
# (line matching ^([-*]|\d+\.)\s , no leading whitespace), outside fenced code blocks;
# lines inside |tables| are not counted, and indented sub-items are not counted.
def clause_count(text):
    n, fence = 0, False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or line.lstrip().startswith("|"):
            continue
        if re.match(r"^([-*]|\d+\.)\s", line):
            n += 1
    return n

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None

def spearman(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 4:
        return None, n
    xs, ys = zip(*pairs)
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return None, n
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return (num / den if den else None), n

meta = {}
for t in TASKS:
    p = (ROOT / "tasks-v4" / t / "prompt.md").read_text(encoding="utf-8")
    test = (ROOT / "tasks-v4" / t / "test.py").read_text(encoding="utf-8")
    m = re.search(r"^TOTAL\s*=\s*(\d+)", test, re.M)
    b = len(p.encode("utf-8"))
    meta[t] = {"bytes": b, "tokens": b // 4, "clauses": clause_count(p),
               "m": int(m.group(1)) if m else None}

fp8 = json.load(open(ROOT / "results/v4-ref-medium-1800.json"))["qwen/qwen3.8-27b"]["runs"]
grades = {}
for name, path in [("sonnet", "results/sonnet-v4/grades.json"),
                   ("haiku", "results/haiku-v4/grades.json"),
                   ("luna", "results/codex-luna-v4/grades.json")]:
    g = json.load(open(ROOT / path))
    grades[name] = {}
    for t in TASKS:
        vs = [v for k, v in g.items() if k.split("/")[0] == t]
        if vs:
            grades[name][t] = (mean([v["pass"] for v in vs]), mean([v["score"] for v in vs]), len(vs))
local = json.load(open(ROOT / "results/v4-local-medium.json"))["q27-Q2_K_L"]["runs"]
v5 = json.load(open(ROOT / "results/v5-smoke-q27-Q3_K_S.json"))["q27-Q3_K_S"]["runs"]

models = {"fp8": {}, **grades, "local-Q2_K_L": {}, "local-Q3_K_S*": {}}
for t in TASKS:
    vs = [r for r in fp8 if r["task"] == t]
    if vs:
        models["fp8"][t] = (mean([r["pass"] for r in vs]), mean([r["score"] for r in vs]), len(vs))
    vs = [r for r in local if r["task"] == t]
    if vs:
        models["local-Q2_K_L"][t] = (mean([r["pass"] for r in vs]), mean([r["score"] for r in vs]), len(vs))
    vs = [r for r in v5 if r["task"] == t]
    if vs:
        models["local-Q3_K_S*"][t] = (mean([r["pass"] for r in vs]), mean([r["score"] for r in vs]), len(vs))

# ---- per-task table ----
order = {"fp8": "fp8 ref", "sonnet": "sonnet", "haiku": "haiku", "luna": "luna",
         "local-Q2_K_L": "local Q2", "local-Q3_K_S*": "local Q3*"}
print("table: task | bytes | ~tok | clauses | m || per model: pass%%/meanSCORE")
for t in TASKS:
    md = meta[t]
    cells = []
    for name in ["fp8", "sonnet", "haiku", "luna", "local-Q2_K_L", "local-Q3_K_S*"]:
        if t in models[name]:
            pr, sc, n = models[name][t]
            cells.append(f"{order[name]} {pr*100:.0f}%/{sc:.2f}({n})")
    print(f"{t} | {md['bytes']} | {md['tokens']} | {md['clauses']} | {md['m']} || " + ", ".join(cells))

# ---- correlations ----
print("\n== Spearman rho vs mean SCORE (per model over that model's tasks; pooled over all task-model pairs) ==")
for metric in ("bytes", "clauses", "m"):
    row = []
    pooled_x, pooled_y = [], []
    for name in ["fp8", "sonnet", "haiku", "luna", "local-Q2_K_L", "local-Q3_K_S*"]:
        ts = [t for t in TASKS if t in models[name]]
        rho, n = spearman([meta[t][metric] for t in ts], [models[name][t][1] for t in ts])
        row.append(f"{order[name]}={rho if rho is None else round(rho,2)}(n={n})")
        pooled_x += [meta[t][metric] for t in ts]
        pooled_y += [models[name][t][1] for t in ts]
    rho, n = spearman(pooled_x, pooled_y)
    print(f"{metric:8s} " + " ".join(row) + f"  POOLED={rho if rho is None else round(rho,2)}(n={n})")

print("\n== fp8: prompt length vs out_tokens (per run, n runs) ==")
for metric in ("bytes", "clauses", "m"):
    rho, n = spearman([meta[r["task"]][metric] for r in fp8], [r.get("out_tokens") for r in fp8])
    print(f"{metric} vs out_tokens: rho={rho if rho is None else round(rho,2)} (n={n})")

# ---- failure spread: distinct failed check names per failed run ----
def fail_names(grader):
    m = re.search(r"FAIL\s*(\[[^\n]*)", grader or "", re.S)
    if not m:
        return []
    # the harness prints a python list of quoted check names
    return re.findall(r"'([^']{4,})'", m.group(1))

print("\n== failure spread: failed runs x mean distinct failed-check names in FAIL list (max 10 shown by harness) ==")
for name in ["sonnet", "haiku", "luna"]:
    g = json.load(open(ROOT / {"sonnet": "results/sonnet-v4/grades.json",
                               "haiku": "results/haiku-v4/grades.json",
                               "luna": "results/codex-luna-v4/grades.json"}[name]))
    spread = []
    for k, v in g.items():
        if k.split("/")[0] not in TASKS or v["pass"]:
            continue
        fn = [f for f in fail_names(v["grader"]) if "timed out" not in f and f != "not run"]
        if fn:
            spread.append(len(fn))
    if spread:
        print(f"{name}: failed runs={len(spread)}, mean distinct failed checks={mean(spread):.1f}, max={max(spread)}")

print("fp8 failed runs w/ >1 distinct failed check:",
      sum(1 for r in fp8 if not r["pass"] and r["score"] not in (None, 0.0)))
print("local-Q2_K_L: per-task mean scores:", {t: models["local-Q2_K_L"][t][1] for t in models["local-Q2_K_L"]})
print("local-Q3_K_S*: scores:", {t: models["local-Q3_K_S*"][t][1] for t in models["local-Q3_K_S*"]})
print("\nmeta:", json.dumps(meta))
