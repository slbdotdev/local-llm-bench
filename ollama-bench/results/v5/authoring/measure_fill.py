"""Report achieved context fill per task from the model's own reported prompt tokens.

Padding written to disk is NOT fill. Filler only enters the context if the agent reads it,
so the honest number is the model's reported prompt size, not the bytes on disk.

Effective prompt tokens for a message = input_tokens + cache_read_input_tokens
+ cache_creation_input_tokens (cached prompt tokens are still prompt tokens).
Achieved fill for a run = the peak of that across the run's assistant messages.

Usage: measure_fill.py <tasks-output-dir> <sandbox-substring>
"""
import json, os, sys, glob, re


def peak_prompt_tokens(path):
    peak = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = ev.get("message")
            if not isinstance(msg, dict):
                continue
            u = msg.get("usage")
            if not isinstance(u, dict):
                continue
            tot = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) \
                + (u.get("cache_creation_input_tokens") or 0)
            peak = max(peak, tot)
    return peak


def main():
    outdir, needle = sys.argv[1], sys.argv[2]
    rows = {}
    for f in glob.glob(os.path.join(outdir, "*.output")):
        try:
            head = open(f, encoding="utf-8", errors="replace").read(400000)
        except OSError:
            continue
        if needle not in head:
            continue
        m = re.search(re.escape(needle) + r"/(\w+)", head)
        if not m:
            continue
        task = m.group(1)
        pk = peak_prompt_tokens(f)
        # Several files can mention a task; keep the run that actually did the work.
        if pk > rows.get(task, (0,))[0]:
            rows[task] = (pk, os.path.basename(f))
    for t in sorted(rows):
        print(f"{t}  peak_prompt_tokens={rows[t][0]}")
    if rows:
        vals = [v[0] for v in rows.values()]
        print(f"\nn={len(vals)}  min={min(vals)}  median={sorted(vals)[len(vals)//2]}  max={max(vals)}")


if __name__ == "__main__":
    main()
