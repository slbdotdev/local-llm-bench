"""Report possible contamination in the endgame arms."""

import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARMS = (
    "Hlineno-tiny", "base-large", "Hlineno-large",
    "base-tiny-high", "Hlineno-tiny-high", "base-large-high", "Hlineno-large-high",
)


def label(run):
    return "%s#%s" % (run.get("task", "?"), run.get("trial", "?"))


def load(tag):
    with open(os.path.join(HERE, tag + ".json"), encoding="utf-8") as stream:
        return json.load(stream)["glm-5.3-flash"]["runs"]


def main(tags):
    for tag in tags:
        runs = load(tag)
        error = [r for r in runs if r.get("stop_reasons", {}).get("error")]
        nonzero = [r for r in runs if r.get("rc", 0) != 0]
        empty = [r for r in runs if r.get("tool_calls", 0) == 0 and r.get("out_tokens", 0) == 0]
        rate_limited = [
            r for r in error
            if r.get("tool_calls", 0) == 0 and r.get("out_tokens", 0) == 0
        ]
        print("%s:" % tag)
        print("  cells: %d" % len(runs))
        print("  cells with an error stop reason: %d%s" % (
            len(error), " (" + ", ".join(label(r) for r in error) + ")" if error else ""))
        print("  cells with rc != 0: %d%s" % (
            len(nonzero), " (" + ", ".join(label(r) for r in nonzero) + ")" if nonzero else ""))
        print("  cells with zero tool calls and zero output tokens: %d%s" % (
            len(empty), " (" + ", ".join(label(r) for r in empty) + ")" if empty else ""))
        print("  rate-limited cells excluded from results: %d%s" % (
            len(rate_limited), " (" + ", ".join(label(r) for r in rate_limited) + ")"
            if rate_limited else ""))


if __name__ == "__main__":
    main(sys.argv[1:] or DEFAULT_ARMS)
