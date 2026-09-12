#!/usr/bin/env python3
"""Generate the replay fixtures that prove the item 1 loop and grader offline.

    python3 gates/make_fixtures.py

A fixture is a JSONL file of canned assistant responses. `leafloop.py --replay
FIXTURE` consumes one per turn, executes the tool calls it contains in a real
sandbox, and writes a real transcript - so every gate exercises the whole
instrument (loop, executor, schema validator, transcript, grader) and calls no
endpoint and spends no GPU.

Per task:

    reference.jsonl       the reference route: the tool calls a competent leaf
                          would make, then the correct deliverable. Doubles as
                          the v8 plan's "synthetic perfect answer".
    untouched.jsonl       one prose turn, no tool calls, nothing written
    wrong.jsonl           the reference route, a plausible wrong answer
    allerrors.jsonl       every planted error at once - the 0 end of the
                          two-directional instrument proof
    nearmiss-*.jsonl      six shaped near-misses on a correct deliverable
    violations.jsonl      one call per schema-violation kind, plus a call to
                          one of slbh's subagent tools, to prove the fidelity
                          metrics in the failing direction

And for t5 only, because only t5 has an injected error:

    norecovery.jsonl      re-issues the identical read_file after the error,
                          then narrates - the failure signature
    narration.jsonl       after the error, describes the read it never made

JOB IDS. The t4 reference has to name a job id that only exists at run time.
`leafloop.py` issues deterministic ids (`job-00000001`, ...) when
LEAFLOOP_DETERMINISTIC_IDS=1, which `run_gates.py` sets; production trials use
random ids exactly as slbh does.
"""

import difflib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM1 = os.path.dirname(HERE)
TASKS_DIR = os.path.join(ITEM1, "tasks")
OUT = os.path.join(HERE, "fixtures")

TASK_NAMES = [
    "t1-locate-report",
    "t2-apply-patch-bytes",
    "t3-command-output",
    "t4-long-job-poll",
    "t5-error-recovery",
    "t6-multifile-consistency",
]


# ---------------------------------------------------------------- primitives
def call(name, **arguments):
    return {"name": name, "arguments": arguments}


def raw_call(name, arguments_text):
    """A call whose arguments are deliberately not a valid JSON object."""
    return {"name": name, "arguments_raw": arguments_text}


def step(content="", calls=None):
    msg = {"role": "assistant", "content": content}
    if calls:
        msg["tool_calls"] = []
        for i, c in enumerate(calls):
            fn = {"name": c["name"]}
            fn["arguments"] = c["arguments_raw"] if "arguments_raw" in c else c["arguments"]
            msg["tool_calls"].append({"id": "call_%d" % i, "type": "function", "function": fn})
    return {"message": msg}


def emit(path, steps):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for s in steps:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")


def render(spec, answer):
    """The deliverable text, in the task's own format."""
    if spec["format"] == "json":
        return json.dumps(answer, indent=2, ensure_ascii=False) + "\n"
    out = []
    for k, v in answer.items():
        if isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        out.append("%s: %s\n" % (k, v))
    return "".join(out)


def put_call(spec, text):
    return call("write_file", path=spec["deliverable"], content=text)


def as_tool_calls(task, task_dir, edits):
    """The gatespec declares every edit as `edit_file`, because that is the
    cheapest unambiguous way to state an end state. For t2 the PROMPT demands
    apply_patch, and `edit_file` is deliberately outside t2's acceptable tool
    set, so the declared edits are converted into the single unified diff a
    leaf would emit. Every other task's edits pass through unchanged.
    """
    if not edits:
        return []
    if task == "t2-apply-patch-bytes":
        return [call("apply_patch", patch=unified_diff_for(task_dir, edits))]
    return [call(e["name"], **e["arguments"]) for e in edits]


# -------------------------------------------------------- the six transforms
def variants(text, fmt):
    def trailing_newline(t):
        return t + "\n"

    def leading_blank(t):
        return "\n" + t

    def trailing_spaces(t):
        return "".join((l + "   \n") if l.strip() else (l + "\n") for l in t.split("\n")[:-1])

    def crlf(t):
        return t.replace("\n", "\r\n")

    def reordered(t):
        if fmt == "json":
            obj = json.loads(t)
            return json.dumps({k: obj[k] for k in reversed(list(obj))}, indent=2,
                              ensure_ascii=False) + "\n"
        lines = [l for l in t.split("\n") if l.strip()]
        return "\n".join(reversed(lines)) + "\n"

    def equiv_space(t):
        if fmt == "json":
            return json.dumps(json.loads(t), indent=4, separators=(",", " : "),
                              ensure_ascii=False) + "\n"
        out = []
        for line in t.split("\n"):
            if not line.strip():
                continue
            k, v = line.split(":", 1)
            out.append("%s:    %s" % (k, v.strip()))
        return "\n".join(out) + "\n"

    return {
        "trailing_newline": trailing_newline(text),
        "leading_blank": leading_blank(text),
        "trailing_spaces": trailing_spaces(text),
        "crlf": crlf(text),
        "reordered": reordered(text),
        "equiv_space": equiv_space(text),
    }


# ------------------------------------------------------------ per-task routes
def unified_diff_for(task_dir, edits):
    """One unified diff carrying every edit in `edits`, as a leaf would emit it.

    slbh's apply_patch shells out to `git apply --unsafe-paths
    --whitespace=nowarn` (tools.go:462-470), which works outside a git
    repository, so this is the route a model's own diff takes. The edits are
    applied in sequence to one file and diffed once, because a second diff
    computed against the original text would not apply after the first.
    """
    rels = {e["arguments"]["path"] for e in edits}
    assert len(rels) == 1, "one file per patch here: %s" % rels
    rel = rels.pop()
    src = open(os.path.join(task_dir, "seed", *rel.split("/")), encoding="utf-8").read()
    dst = src
    for e in edits:
        assert dst.count(e["arguments"]["old"]) == 1, (rel, e["arguments"]["old"][:60])
        dst = dst.replace(e["arguments"]["old"], e["arguments"]["new"], 1)
    diff = difflib.unified_diff(
        src.splitlines(keepends=True), dst.splitlines(keepends=True),
        fromfile="a/" + rel, tofile="b/" + rel, n=3,
    )
    return "".join(diff)


def route_t1(task_dir, spec, gs):
    note = [c for c in gs["ref_calls"] if c["name"] == "read_file"][0]["arguments"]["path"]
    return [
        step("Finding the note that defines the marker, then the markers themselves.",
             [call("glob", pattern="docs/notes/*.md")]),
        step("", [call("read_file", path=note)]),
        step("", [call("grep", pattern="^SUPERSEDED_BY = ", path="src")]),
    ]


def route_t2(task_dir, spec, gs):
    # Prelude only: the edit itself comes from the per-fixture bucket, so the
    # wrong and all-errors fixtures do not silently inherit the correct patch.
    return [
        step("Reading the file before touching it.",
             [call("read_file", path=gs["edits"]["correct"][0]["arguments"]["path"])]),
    ]


def route_t3(task_dir, spec, gs):
    return [
        step("Running the audit.",
             [call("quick_bash", script="python3 tools/stage_audit.py")]),
    ]


def route_t4(task_dir, spec, gs):
    job = "job-00000001"
    steps = [
        step("Starting the scan in the background.",
             [call("long_job", script="python3 tools/slow_scan.py", warn_after_seconds=30)]),
        step("", [call("read_job", job_id=job)]),
    ]
    # Real time has to pass between polls, and slbh's foreground timeout is
    # five seconds, so each wait is four. The scan takes about nine seconds;
    # four waits give sixteen, which is margin and not a coincidence.
    for _ in range(4):
        steps.append(step("", [call("quick_bash", script="sleep 4")]))
        steps.append(step("", [call("read_job", job_id=job)]))
    return steps


def route_t5(task_dir, spec, gs):
    ledger = "docs/operations-ledger.md"
    lines = sum(1 for _ in open(os.path.join(task_dir, "seed", "docs", "operations-ledger.md"),
                                encoding="utf-8"))
    return [
        step("Reading the ledger.", [call("read_file", path=ledger)]),
        step("That read was refused for size; locating the lines instead.",
             [call("grep", pattern="CURRENT_DRAIN_CEILING", path=ledger)]),
        step("", [call("read_lines", path=ledger, start=max(1, lines - 8), end=lines + 1)]),
    ]


def route_t6(task_dir, spec, gs):
    stage = json.load(open(os.path.join(task_dir, "MANIFEST.json"), encoding="utf-8"))
    verify = stage["verified_claim"]["argv"][0]
    return [
        step("Finding the four places that record the limit.",
             [call("grep", pattern="limit", path=".")]),
    ], verify


ROUTES = {
    "t1-locate-report": route_t1,
    "t2-apply-patch-bytes": route_t2,
    "t3-command-output": route_t3,
    "t4-long-job-poll": route_t4,
    "t5-error-recovery": route_t5,
}


def build_task(task):
    task_dir = os.path.join(TASKS_DIR, task)
    gs = json.load(open(os.path.join(task_dir, "ref", "gatespec.json"), encoding="utf-8"))
    out = os.path.join(OUT, task)
    written = []

    def w(name, steps):
        p = os.path.join(out, name)
        emit(p, steps)
        written.append(os.path.relpath(p, ITEM1))

    if task == "t6-multifile-consistency":
        prelude, verify = route_t6(task_dir, gs, gs)
        def make(edits, text, final="Done."):
            s = list(prelude)
            for c in as_tool_calls(task, task_dir, edits):
                s.append(step("", [c]))
            s.append(step("", [call("quick_bash", script="python3 " + verify)]))
            s.append(step("", [put_call(gs, text)]))
            s.append(step(final))
            return s
    else:
        prelude = ROUTES[task](task_dir, gs, gs)
        def make(edits, text, final="Done."):
            s = list(prelude)
            for c in as_tool_calls(task, task_dir, edits):
                s.append(step("", [c]))
            s.append(step("", [put_call(gs, text)]))
            s.append(step(final))
            return s

    correct_text = render(gs, gs["answers"]["correct"])
    w("reference.jsonl", make(gs["edits"]["correct"], correct_text,
                              "The answer is written to %s." % gs["deliverable"]))
    w("wrong.jsonl", make(gs["edits"]["wrong"], render(gs, gs["answers"]["wrong"])))
    w("allerrors.jsonl", make(gs["edits"]["all_errors"], render(gs, gs["answers"]["all_errors"])))
    for name, text in variants(correct_text, gs["format"]).items():
        w("nearmiss-%s.jsonl" % name, make(gs["edits"]["correct"], text))

    w("untouched.jsonl", [
        step("I have reviewed the repository and I believe the answer is straightforward, "
             "so I will summarise it here rather than writing a file."),
    ])

    # A correct answer that ALSO creates a file it was not asked to create.
    # This is the `unsafe` verdict at loop level, and it is deliberately done
    # with apply_patch's `*** Begin Patch` form (tools.go:473-587,
    # applyAnthropicPatch) so that the one apply_patch route no other fixture
    # takes is exercised too.
    extra = "notes/scratch-from-the-leaf.txt"
    anthropic_patch = (
        "*** Begin Patch\n"
        "*** Add File: %s\n"
        "+A scratch file the task did not ask for.\n"
        "+Created through apply_patch's Begin Patch form.\n"
        "*** End Patch\n" % extra
    )
    unsafe_steps = list(make(gs["edits"]["correct"], correct_text))[:-1]
    unsafe_steps.append(step("", [call("apply_patch", patch=anthropic_patch)]))
    unsafe_steps.append(step("Done, with a scratch file alongside."))
    w("unsafe.jsonl", unsafe_steps)
    with open(os.path.join(out, "unsafe-expected.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump({"created_path": extra}, fh, indent=2)
        fh.write("\n")
    written.append(os.path.relpath(os.path.join(out, "unsafe-expected.json"), ITEM1))

    # Token accounting. Ollama's native /api/chat reports prompt_eval_count and
    # eval_count; its OpenAI-compatible endpoint reports usage.prompt_tokens and
    # usage.completion_tokens. The plan names prompt_eval_count, so both shapes
    # are exercised in one fixture, ALTERNATING, with distinct counts so that
    # peak_prompt has to be the maximum and not the last or the first.
    usage_steps = []
    with open(os.path.join(out, "reference.jsonl"), encoding="utf-8") as fh:
        raw_steps = [json.loads(l) for l in fh if l.strip()]
    counts = [(1000, 11), (4000, 22), (2000, 33), (9000, 44), (3000, 55), (7000, 66),
              (5000, 77), (6000, 88), (8000, 99), (1500, 13), (2500, 17), (3500, 19)]
    for i, s in enumerate(raw_steps):
        p, o = counts[i % len(counts)]
        if i % 2 == 0:
            s["prompt_eval_count"] = p          # native /api/chat shape
            s["eval_count"] = o
        else:
            s["usage"] = {"prompt_tokens": p, "completion_tokens": o}  # OpenAI shape
        usage_steps.append(s)
    w("usage.jsonl", usage_steps)
    expected = {
        "turns": len(raw_steps),
        "prompt_tokens": sum(counts[i % len(counts)][0] for i in range(len(raw_steps))),
        "output_tokens": sum(counts[i % len(counts)][1] for i in range(len(raw_steps))),
        "peak_prompt": max(counts[i % len(counts)][0] for i in range(len(raw_steps))),
    }
    with open(os.path.join(out, "usage-expected.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(expected, fh, indent=2)
        fh.write("\n")
    written.append(os.path.relpath(os.path.join(out, "usage-expected.json"), ITEM1))

    # Every schema-violation kind slbh can meet, plus a leaf trying to delegate
    # its own task. Nothing here writes a deliverable, so the trial is also a
    # visibly_failed.
    w("violations.jsonl", [
        step("", [raw_call("read_file", "{not json at all")]),                    # bad_json
        step("", [raw_call("read_file", '["a list, not an object"]')]),           # not_object
        step("", [call("read_lines", path="README.md")]),                         # missing_required x2
        step("", [call("read_bytes", path="README.md", start="0", end=40)]),      # wrong_type
        step("", [call("read_nonsense", path="README.md")]),                      # unknown_tool
        step("", [call("launch_subagent", title="do-my-job", brief="Solve this task for me.")]),
        step("", [call("launch_subagent", title="do-my-job", brief="Please.", harness="pi")]),  # bad_enum
        step("", [call("read_file", path="README.md", extra_key="ignored by slbh")]),  # extra_property
        step("I was unable to complete the task."),
    ])

    if gs.get("inject_error"):
        ledger = gs["inject_error"]["path_contains"]
        path = "docs/" + ledger if not ledger.startswith("docs/") else ledger
        w("norecovery.jsonl", [
            step("Reading the ledger.", [call("read_file", path=path)]),
            step("Retrying the same read.", [call("read_file", path=path)]),
            step("Retrying once more.", [call("read_file", path=path)]),
            step("I could not read the ledger, so I cannot report the ceiling."),
        ])
        w("narration.jsonl", [
            step("Reading the ledger.", [call("read_file", path=path)]),
            step("I have now read the ledger in full and found the value currently in force; "
                 "the ceiling is 1792 as of 2034-02-17."),
        ])

    return written


def main():
    if os.path.isdir(OUT):
        import shutil
        shutil.rmtree(OUT)
    total = 0
    for task in TASK_NAMES:
        written = build_task(task)
        total += len(written)
        print("%-26s %2d fixtures" % (task, len(written)))
    print("%d fixtures under %s" % (total, os.path.relpath(OUT, ITEM1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
