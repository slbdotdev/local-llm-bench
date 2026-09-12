#!/usr/bin/env python3
"""Render a slot as one self-contained single-shot prompt, material inlined.

    python3 render_prompt.py slots/a1-summarise-r1            # to stdout
    python3 render_prompt.py slots/a1-summarise-r1 --measure   # chars/tokens only

## Why this exists, and when to use which mode

An item-3 slot can be run two ways, and they measure different things.

**Agentic mode** (`pibench.py`): the seed is copied into a sandbox, the model reads it with tools
and writes the deliverable as a file. This is the v7 task format and the mode the six slots are
authored for. Its occupancy is whatever the model chose to read, which is exactly the effect
D7-32 named — "the model now sets the material aside by never opening it" — so a trial's
`peak_prompt` here is a finding about the model's reading, not a property of the cell.

**Single-shot mode** (this renderer): the prompt carries every seed file inline, in a
deterministic order, and the answer is the model's text. Occupancy is then guaranteed by
construction, `peak_prompt` is comparable with item 2's rungs, and the v8 plan's void rule
(section 4: a cell is void if it misses its rung by more than 15%) becomes applicable to this
family. `batch_cell.py` and `escalate.py` both use this mode, the first because fifty small jobs
back to back cannot each afford an agentic loop, the second because a hosted arm has to be
handed the same material the local arm saw.

The deliverable instruction is rewritten for the mode: there is no filesystem to write to, so the
answer is the file's contents between two fences. Everything else in `prompt.md` is passed
through byte for byte, so the two modes cannot drift apart on the task itself.
"""
import argparse
import json
import os
import sys

CHARS_PER_TOKEN = 4.664

SINGLE_SHOT_HEADER = """You are answering in one turn. There is no filesystem and no tools: all
of the material is below, under `## Material`, with each file named by the path it would have had
in the workspace.

The task is stated next, exactly as it is given in the file-based form of this job. Follow it in
full, with one change: instead of writing the deliverable to a file, print the deliverable — and
nothing else — between a line containing only `===BEGIN {deliverable}===` and a line containing
only `===END {deliverable}===`. Write no commentary, no preamble and no reasoning outside those
two markers.

---

"""

MATERIAL_HEADER = """

---

## Material

Each file below is given as it is, between its own markers. Nothing outside this section is part
of the material.

"""


def seed_files(slot):
    seed = os.path.join(slot, "seed")
    out = []
    for dirpath, dirnames, filenames in os.walk(seed):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            out.append((os.path.relpath(p, seed).replace(os.sep, "/"), p))
    return sorted(out)


def render(slot):
    with open(os.path.join(slot, "prompt.md"), "r", encoding="utf-8") as fh:
        prompt = fh.read()
    with open(os.path.join(slot, "MANIFEST.json"), "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    parts = [SINGLE_SHOT_HEADER.format(deliverable=manifest["deliverable"]), prompt,
             MATERIAL_HEADER]
    for rel, path in seed_files(slot):
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
        parts.append("===FILE %s===\n%s\n===ENDFILE %s===\n\n" % (rel, body.rstrip("\n"), rel))
    return "".join(parts)


def extract_answer(text, deliverable):
    """Pull the deliverable out of a single-shot reply. Returns None when the markers are absent.

    Tolerant on purpose: the markers may carry stray backticks, whitespace or case, because none
    of that is what is being measured. A reply with no markers at all is returned whole, so a
    model that simply answered without them is graded on its answer rather than failed on its
    formatting — the grader's own shape subcheck is what decides whether it said anything.
    """
    begin, end = "===BEGIN %s===" % deliverable, "===END %s===" % deliverable
    low = (text or "")
    i = low.find(begin)
    if i < 0:
        return text
    i += len(begin)
    j = low.find(end, i)
    body = low[i:] if j < 0 else low[i:j]
    return body.strip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slot")
    ap.add_argument("--measure", action="store_true", help="print the size only")
    args = ap.parse_args()
    text = render(args.slot)
    if args.measure:
        print(json.dumps({"slot": os.path.basename(args.slot.rstrip("/")),
                          "prompt_chars": len(text),
                          "prompt_tokens_est": round(len(text) / CHARS_PER_TOKEN),
                          "chars_per_token": CHARS_PER_TOKEN,
                          "seed_files": len(seed_files(args.slot))}, indent=1))
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
