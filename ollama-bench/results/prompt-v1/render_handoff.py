"""Render the ledger table and quota table for the handoff. usage: render_handoff.py"""
import json, os, statistics, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]

ARMS = [
    ("base-tiny",    "baseline",  "pi's default prompt, verbatim (control)"),
    ("H-tiny",       "H",         "+ the five published QuixBugs guidelines"),
    ("Hlineno-tiny", "Hlineno",   "+ those five and the line-number rule"),
]
HOLD = [("base-large", "baseline"), ("Hlineno-large", "Hlineno")]
ARMS_HIGH = [
    ("base-tiny-high", "baseline", "pi's default prompt, verbatim (control)"),
    ("Hlineno-tiny-high", "Hlineno", "+ those five and the line-number rule"),
]
HOLD_HIGH = [("base-large-high", "baseline"), ("Hlineno-large-high", "Hlineno")]


def runs(tag):
    p = os.path.join(HERE, tag + ".json")
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))["glm-5.3-flash"]["runs"]


def row(tag, name, hyp, hold_tag=None):
    r = runs(tag)
    if not r:
        return None
    n, p = len(r), sum(x["pass"] for x in r)
    cw = sum(1 for x in r if x.get("verdict") == "confidently_wrong")
    out = statistics.mean(x["out_tokens"] for x in r)
    h = runs(hold_tag) if hold_tag else []
    hs = "%d/%d" % (sum(x["pass"] for x in h), len(h)) if h else "not run"
    return "| `%s` | %s | %d/%d | %d | %.0f | %s |" % (name, hyp, p, n, cw, out, hs)


lines = ["| variant | hypothesis | tiny pass | confidently wrong | mean out tok | large pass |",
         "|---|---|---:|---:|---:|---:|"]
for tag, name, hyp in ARMS:
    hold = dict((n, t) for t, n in HOLD).get(name)
    r = row(tag, name, hyp, hold)
    if r:
        lines.append(r)
for name, hyp in [("verify", "run the task's own checker until it passes"),
                  ("lineno", "the line-number rule alone"),
                  ("outfmt", "the output file's format is part of the answer"),
                  ("spec", "read the named source of truth end to end first"),
                  ("exhaust", "check the finished output against every stated clause"),
                  ("minimal", "H's minimality bullets alone"),
                  ("nodocs", "drop pi's own documentation block")]:
    if not runs(name + "-tiny"):
        lines.append("| `%s` | %s | not run | - | - | not run |" % (name, hyp))
print("\n".join(lines))

print("\n\n### Per task, tiny band (passes / trials)\n")
hdr = "| arm | " + " | ".join(TASKS) + " |"
print(hdr); print("|---|" + "---|" * len(TASKS))
for tag, name, _ in ARMS:
    r = runs(tag)
    if not r:
        continue
    cells = []
    for t in TASKS:
        rs = [x for x in r if x["task"] == t]
        cells.append("%d/%d" % (sum(x["pass"] for x in rs), len(rs)) if rs else "-")
    print("| `%s` | %s |" % (name, " | ".join(cells)))

print("\n\n### Cost and stability, tiny band\n")
print("| arm | mean in tok | mean out tok | mean wall s | mean turns | mean tool calls | timeouts | error turns |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for tag, name, _ in ARMS:
    r = runs(tag)
    if not r:
        continue
    print("| `%s` | %.0f | %.0f | %.0f | %.1f | %.1f | %d | %d |" % (
        name, statistics.mean(x["in_tokens"] for x in r), statistics.mean(x["out_tokens"] for x in r),
        statistics.mean(x["wall_s"] for x in r), statistics.mean(x["turns"] for x in r),
        statistics.mean(x["tool_calls"] for x in r),
        sum(1 for x in r if x["timed_out"]),
        sum(1 for x in r if x.get("stop_reasons", {}).get("error"))))

print("\n\n### Every failure, both bands\n")
for tag, name, _ in ARMS + [(t, n, "") for t, n in HOLD]:
    for x in runs(tag):
        if x["pass"]:
            continue
        g = " / ".join(x["grader"].splitlines())[:150]
        print("- `%s` %s trial%s — %s, score %s%s: %s" % (
            name, x["task"], x["trial"], x.get("verdict"), x.get("score"),
            " TIMEOUT" if x["timed_out"] else "", g))

print("\n\n## Ledger at --think high\n")
lines = ["| variant | hypothesis | tiny pass | confidently wrong | mean out tok | large pass |",
         "|---|---|---:|---:|---:|---:|"]
for tag, name, hyp in ARMS_HIGH:
    hold = dict((n, t) for t, n in HOLD_HIGH).get(name)
    r = row(tag, name, hyp, hold)
    if r:
        lines.append(r)
print("\n".join(lines))

print("\n\n### Per task, tiny band at --think high (passes / trials)\n")
hdr = "| arm | " + " | ".join(TASKS) + " |"
print(hdr); print("|---|" + "---|" * len(TASKS))
for tag, name, _ in ARMS_HIGH:
    r = runs(tag)
    if not r:
        continue
    cells = []
    for t in TASKS:
        rs = [x for x in r if x["task"] == t]
        cells.append("%d/%d" % (sum(x["pass"] for x in rs), len(rs)) if rs else "-")
    print("| `%s` | %s |" % (name, " | ".join(cells)))

print("\n\n### Cost and stability, tiny band at --think high\n")
print("| arm | mean in tok | mean out tok | mean wall s | mean turns | mean tool calls | timeouts | error turns |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for tag, name, _ in ARMS_HIGH:
    r = runs(tag)
    if not r:
        continue
    print("| `%s` | %.0f | %.0f | %.0f | %.1f | %.1f | %d | %d |" % (
        name, statistics.mean(x["in_tokens"] for x in r), statistics.mean(x["out_tokens"] for x in r),
        statistics.mean(x["wall_s"] for x in r), statistics.mean(x["turns"] for x in r),
        statistics.mean(x["tool_calls"] for x in r),
        sum(1 for x in r if x["timed_out"]),
        sum(1 for x in r if x.get("stop_reasons", {}).get("error"))))

print("\n\n### Every failure, both bands at --think high\n")
for tag, name, _ in ARMS_HIGH + [(t, n, "") for t, n in HOLD_HIGH]:
    for x in runs(tag):
        if x["pass"]:
            continue
        g = " / ".join(x["grader"].splitlines())[:150]
        print("- `%s` %s trial%s — %s, score %s%s: %s" % (
            name, x["task"], x["trial"], x.get("verdict"), x.get("score"),
            " TIMEOUT" if x["timed_out"] else "", g))

print("\n\n### Quota readings\n")
print("Readings are in `logs/quota.log` and `quota/*.json`, 150 s apart.")
