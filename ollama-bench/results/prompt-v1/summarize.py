"""Ledger rows for prompt-v1 arms. usage: summarize.py <tag> [<tag>...]"""
import json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]

def load(tag):
    with open(os.path.join(HERE, tag + ".json"), encoding="utf-8") as f:
        return json.load(f)["glm-5.3-flash"]["runs"]

hdr = ("| arm | pass | " + " | ".join(TASKS) + " | conf-wrong | vis-fail | mean out tok |"
       " mean in tok | mean wall s | mean turns | mean tools | timeouts | length stops |")
print(hdr); print("|" + "---|" * (hdr.count("|") - 1))
for tag in sys.argv[1:]:
    runs = load(tag)
    n = len(runs); p = sum(r["pass"] for r in runs)
    cells = []
    for t in TASKS:
        rs = [r for r in runs if r["task"] == t]
        cells.append("%d/%d" % (sum(r["pass"] for r in rs), len(rs)) if rs else "-")
    cw = sum(1 for r in runs if r.get("verdict") == "confidently_wrong")
    vf = sum(1 for r in runs if r.get("verdict") == "visibly_failed")
    to = sum(1 for r in runs if r.get("timed_out"))
    ls = sum(r.get("stop_reasons", {}).get("length", 0) for r in runs)
    print("| %s | %d/%d | %s | %d | %d | %.0f | %.0f | %.0f | %.1f | %.1f | %d | %d |" % (
        tag.split("/")[-1], p, n, " | ".join(cells), cw, vf,
        statistics.mean(r["out_tokens"] for r in runs),
        statistics.mean(r["in_tokens"] for r in runs),
        statistics.mean(r["wall_s"] for r in runs),
        statistics.mean(r["turns"] for r in runs),
        statistics.mean(r["tool_calls"] for r in runs), to, ls))

if os.environ.get("PV1_FAILS"):
    for tag in sys.argv[1:]:
        print("\n### failures in %s" % tag)
        for r in load(tag):
            if r["pass"]:
                continue
            print("- %s trial%s verdict=%s score=%s stop=%s wall=%.0f turns=%d tools=%d out=%d%s"
                  % (r["task"], r["trial"], r.get("verdict"), r.get("score"), r.get("stop_reason"),
                     r["wall_s"], r["turns"], r["tool_calls"], r["out_tokens"],
                     " TIMEOUT" if r["timed_out"] else ""))
            print("    grader: " + " / ".join(r["grader"].splitlines())[:400])
