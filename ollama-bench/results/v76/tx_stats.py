"""Per-transcript tool statistics for slbh runtime transcripts.

Usage: python3 v75_tx_stats.py TRANSCRIPT.jsonl [...]

For each transcript: API rounds, tool calls by name, failures by name, and how many
failures carried output beyond the `tool error:` line (the thing e45e9d5 changed).
"""
import collections
import json
import sys


def stats(path):
    rounds = set()
    calls = collections.Counter()
    fails = collections.Counter()
    fails_with_output = collections.Counter()
    bare = collections.Counter()
    usage_out = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = ev.get("kind")
            meta = ev.get("metadata") or {}
            if kind == "inference_request":
                rounds.add(meta.get("round"))
            elif kind == "tool":
                calls[meta.get("name")] += 1
            elif kind == "tool_result":
                name = meta.get("name")
                text = ev.get("text") or ""
                if text.startswith("tool error:"):
                    fails[name] += 1
                    first, _, rest = text.partition("\n")
                    if rest.strip():
                        fails_with_output[name] += 1
                    else:
                        bare[first.strip()] += 1
            elif kind == "usage":
                usage_out += int(meta.get("completion_tokens") or 0)
    return rounds, calls, fails, fails_with_output, bare, usage_out


for path in sys.argv[1:]:
    rounds, calls, fails, fails_with_output, bare, usage_out = stats(path)
    print(f"== {path}")
    print(f"   rounds={len(rounds)} tool_calls={sum(calls.values())} failures={sum(fails.values())} "
          f"failures_with_output={sum(fails_with_output.values())} completion_tokens={usage_out}")
    for name, n in calls.most_common():
        print(f"   {name:16s} calls={n:3d} failed={fails[name]:3d} failed_with_output={fails_with_output[name]:3d}")
    if bare:
        print("   bare failures (no output after the error line):")
        for text, n in bare.most_common(5):
            print(f"     {n:3d}x {text[:100]}")
