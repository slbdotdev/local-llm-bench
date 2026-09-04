"""Quant ranking analysis: mean SCORE per model with a bootstrap CI over tasks, pass rate, timeouts.
Usage: python results/v4-analyse.py [results/v4-local-medium.json] [reps] [ci]
A trial counts as pass only if pass and not timed_out. SCORE missing -> 0.0 (a run that produced nothing
gradable scores nothing). Bootstrap resamples TASKS with replacement (the unit of difficulty), averaging
each task's per-trial scores, so the CI reflects task-to-task spread, not trial noise alone."""
import json, random, statistics, sys
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "results/v4-local-medium.json"
reps = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
ci = float(sys.argv[3]) if len(sys.argv) > 3 else 0.90
d = json.load(open(path, encoding="utf-8"))
rng = random.Random(12)


def score(t):
    if t.get("timed_out") and not t.get("pass"):
        return t.get("score") or 0.0
    s = t.get("score")
    if s is None:
        s = 1.0 if t.get("pass") else 0.0
    return float(s)


rows = []
per_task = {}
task_means_by = {}
for model, r in d.items():
    runs = r.get("runs", [])
    if not runs:
        continue
    by = defaultdict(list)
    for t in runs:
        by[t["task"]].append(t)
    tasks = sorted(by)
    task_means = [statistics.mean(score(t) for t in by[k]) for k in tasks]
    boots = []
    for _ in range(reps):
        sample = [task_means[rng.randrange(len(task_means))] for _ in task_means]
        boots.append(statistics.mean(sample))
    boots.sort()
    lo = boots[int((1 - ci) / 2 * reps)]
    hi = boots[int((1 + ci) / 2 * reps) - 1]
    passes = sum(1 for t in runs if t.get("pass") and not t.get("timed_out"))
    tos = sum(1 for t in runs if t.get("timed_out"))
    wall = statistics.mean(t.get("wall_s", 0) for t in runs)
    clean = [score(t) for t in runs if not t.get("timed_out")]
    cond = statistics.mean(clean) if clean else float("nan")
    rows.append((model, statistics.mean(task_means), lo, hi, passes, len(runs), tos, wall, len(tasks), cond))
    task_means_by[model] = dict(zip(tasks, task_means))
    per_task[model] = {k: (statistics.mean(score(t) for t in by[k]), sum(1 for t in by[k] if t.get("pass") and not t.get("timed_out")), len(by[k])) for k in tasks}

rows.sort(key=lambda x: -x[1])
print(f"| model | mean SCORE | {int(ci*100)}% CI (bootstrap over tasks) | mean SCORE excl. timeouts | pass | timeouts | mean wall s | tasks |")
print("|---|---|---|---|---|---|---|---|")
for m, mean, lo, hi, p, n, tos, wall, nt, cond in rows:
    print(f"| {m} | {mean:.3f} | [{lo:.3f}, {hi:.3f}] | {cond:.3f} | {p}/{n} | {tos} | {wall:.0f} | {nt} |")
print("mean SCORE counts a timed-out run as its recorded partial score (0 if nothing gradable); a quant that is slow")
print("at this config is censored by the shared timeout, so read the excl.-timeouts column and the timeouts count together.")
if len(rows) > 1:
    seps = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            seps.append(f"{a[0]} vs {b[0]}: {'SEPARATED' if a[2] > b[3] else 'tied (CIs overlap)'} [marginal CIs, conservative]")
            common = sorted(set(task_means_by[a[0]]) & set(task_means_by[b[0]]))
            if len(common) >= 2:
                diffs = [task_means_by[a[0]][k] - task_means_by[b[0]][k] for k in common]
                bd = sorted(statistics.mean(diffs[rng.randrange(len(diffs))] for _ in diffs) for _ in range(reps))
                dlo, dhi = bd[int((1 - ci) / 2 * reps)], bd[int((1 + ci) / 2 * reps) - 1]
                verdict = "SEPARATED (paired)" if dlo > 0 or dhi < 0 else "tied (paired CI spans 0)"
                seps.append(f"    paired over {len(common)} common tasks: mean diff {statistics.mean(diffs):+.3f} {int(ci*100)}% CI [{dlo:+.3f}, {dhi:+.3f}] -> {verdict}")
    print("\n" + "\n".join(seps))
all_tasks = sorted({k for m in per_task for k in per_task[m]})
models = [r[0] for r in rows]
print("\n| task | " + " | ".join(models) + " |")
print("|---|" + "---|" * len(models))
for k in all_tasks:
    cells = []
    for m in models:
        v = per_task[m].get(k)
        cells.append(f"{v[1]}/{v[2]} ({v[0]:.2f})" if v else "-")
    print(f"| {k} | " + " | ".join(cells) + " |")
