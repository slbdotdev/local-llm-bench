#!/usr/bin/env python3
"""What the model actually asked the tools for, and what came back.

tx_stats.py counts calls and failures by tool name. That is enough to rank tools and to
see the effect of a change to error formatting, and it was not enough to choose a change:
a call that succeeds and returns nothing useful is invisible to it, and so is a call the
model repeats verbatim because the first one told it nothing.

This adds three things over the counts, all read from the same transcripts:

  * every call's arguments, so a pattern like `**/*.py` is visible as itself;
  * EMPTY successes -- a result of zero non-whitespace bytes, which the v7.5 write-up
    named as the class read_file, read_lines, grep and glob all fall into;
  * REPEATS -- the same (tool, arguments) issued more than once in one session, which is
    what a model does when a result did not answer the question it asked.

Usage:
  python3 v76_calls.py --rows v76base.json --arm slbh_real          aggregate
  python3 v76_calls.py --rows v76base.json --arm slbh_real --dump   every call, in order
  python3 v76_calls.py TRANSCRIPT.jsonl [...]                       transcripts directly
"""
import argparse
import collections
import json
import os


def events(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def calls(path):
    """Yield (tool, arguments, result_text) triples in transcript order.

    A `tool` event carries the arguments; the `tool_result` event that follows carries the
    text. They are paired by call_id where the metadata has one and positionally otherwise,
    because the agent executes a batch's calls one at a time in order.
    """
    pending = []
    for ev in events(path):
        meta = ev.get("metadata") or {}
        if ev.get("kind") == "tool":
            pending.append((meta.get("name"), ev.get("text") or "", meta.get("call_id")))
        elif ev.get("kind") == "tool_result":
            text = ev.get("text") or ""
            call_id = meta.get("call_id")
            index = 0
            for i, (_, _, cid) in enumerate(pending):
                if call_id and cid == call_id:
                    index = i
                    break
            if pending:
                name, args, _ = pending.pop(index)
            else:
                name, args = meta.get("name"), ""
            yield name, args, text


def summarize(paths, dump=False):
    per_tool = collections.Counter()
    empty = collections.Counter()
    failed = collections.Counter()
    repeats = collections.Counter()
    arg_samples = collections.defaultdict(collections.Counter)
    result_bytes = collections.Counter()
    for path in paths:
        seen = collections.Counter()
        for name, args, text in calls(path):
            per_tool[name] += 1
            result_bytes[name] += len(text)
            if text.startswith("tool error:"):
                failed[name] += 1
            elif not text.strip():
                empty[name] += 1
            key = (name, args)
            seen[key] += 1
            if seen[key] == 2:
                repeats[name] += 1
            elif seen[key] > 2:
                repeats[name] += 1
            arg_samples[name][args[:160]] += 1
            if dump:
                flag = "ERR" if text.startswith("tool error:") else ("EMPTY" if not text.strip() else f"{len(text)}b")
                print(f"{os.path.basename(os.path.dirname(path))[:12]:12s} {name:16s} {flag:8s} {args[:150]}")
    return per_tool, empty, failed, repeats, arg_samples, result_bytes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripts", nargs="*")
    ap.add_argument("--rows", default="")
    ap.add_argument("--arm", default="slbh_real")
    ap.add_argument("--label", default=None)
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--args", type=int, default=8, help="how many distinct argument strings to show per tool")
    a = ap.parse_args()

    paths = list(a.transcripts)
    if a.rows:
        for row in json.load(open(a.rows, encoding="utf-8"))["rows"]:
            if row["arm"] != a.arm:
                continue
            if a.label is not None and row.get("label") != a.label:
                continue
            if row.get("transcript") and os.path.exists(row["transcript"]):
                paths.append(row["transcript"])
    if not paths:
        raise SystemExit("no transcripts")

    per_tool, empty, failed, repeats, arg_samples, result_bytes = summarize(paths, a.dump)
    print(f"\n{len(paths)} transcripts, {sum(per_tool.values())} tool calls\n")
    print(f"{'tool':18s} {'calls':>6s} {'failed':>7s} {'empty ok':>9s} {'repeat':>7s} {'result KB':>10s}")
    for name, n in per_tool.most_common():
        print(f"{name:18s} {n:6d} {failed[name]:7d} {empty[name]:9d} {repeats[name]:7d} "
              f"{result_bytes[name]/1024:10.1f}")
    print(f"{'ALL':18s} {sum(per_tool.values()):6d} {sum(failed.values()):7d} {sum(empty.values()):9d} "
          f"{sum(repeats.values()):7d} {sum(result_bytes.values())/1024:10.1f}")
    for name, n in per_tool.most_common():
        print(f"\n-- {name} arguments ({len(arg_samples[name])} distinct)")
        for args, count in arg_samples[name].most_common(a.args):
            print(f"   {count:3d}x {args}")


if __name__ == "__main__":
    main()
