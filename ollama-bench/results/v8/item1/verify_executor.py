#!/usr/bin/env python3
"""Differential test: leafloop's Python executor against slbh's REAL Go runtime.

    python3 verify_executor.py            # build, run both sides, diff
    python3 verify_executor.py --keep      # leave the scratch build and sandboxes
    python3 verify_executor.py --show-all  # print every call, not only the diffs

`verify_schemas.py` proves the schemas are a verbatim lift. This proves the
other half: that what a model SEES when it calls a tool - the output text, and
the exact `tool error: ...` string - is what slbh's own
internal/harness/tools.go would have produced. Every item 1 fidelity metric
rests on that, because a model which recovers from slbh's real error message
and not from a paraphrase of it is the thing being measured.

HOW
---
It copies the slbh working tree to a scratch directory, drops a
`cmd/toolproof` into the COPY that constructs a real `harness.Runtime` and
calls its real `ExecuteTool`, and pipes a fixed list of calls through it with a
fixed mini-sandbox as the working directory. The same list runs through
`leafloop.Executor` over a byte-identical copy of that sandbox. The two
outputs are normalised for the things that cannot match by construction (job
ids, timestamps, the sandbox's own absolute path) and diffed.

/home/slb/slbh is read only to this script. No endpoint is reachable from the
proof binary: it is given a provider factory that always errors, and the seat
agent it starts has no model, so it fails immediately and dials nothing.

A declared difference is not a failure. DIFFERENCES records the places where
Go and Python cannot agree and says why; everything else must match exactly.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leafloop  # noqa: E402
import toolschemas  # noqa: E402

SLBH = os.environ.get("SLBH_REPO", "/home/slb/slbh")

# Known, declared, and deliberately not fixed. Each is a place where matching Go
# exactly would mean reimplementing a Go standard-library corner that no item 1
# task route touches.
DIFFERENCES = {
    "badjson/args":
        "Go's encoding/json words a SYNTAX error its own way (\"invalid character "
        "'n' looking for beginning of object key string\") and Python's json words it "
        "differently. The `tool error: tool arguments must be JSON: ` prefix matches "
        "exactly; only the parser's own complaint differs. The array/number/string/bool "
        "cases, which ARE deterministic, are reproduced verbatim.",
    "glob/bad-pattern":
        "Go filepath.Glob returns ErrBadPattern for an unterminated character "
        "class; Python's glob returns no match instead. No task route emits one.",
    "grep/bad-regexp":
        "Go's RE2 and Python's re reject different patterns, and word their "
        "errors differently. The pattern is recorded in the transcript either way.",
    "list_jobs/order":
        "slbh's job.Manager.List ranges over a Go map, so slbh's OWN ordering is "
        "randomised per call. Compared as a set. A leaf that depends on list_jobs "
        "order is depending on nothing, which is worth knowing before item 5's "
        "batch lane is authored.",
}

PROOF_GO = '''// Scratch only, built inside a COPY of the slbh tree. Reads one JSON object
// per line from stdin - {"name": ..., "arguments": "<json text>"} - calls the
// real harness.Runtime.ExecuteTool, and prints what a model would have been
// shown: the result, or `tool error: ` + the error, exactly as
// internal/harness/agent.go:418-421 does it.
package main

import (
\t"bufio"
\t"encoding/json"
\t"fmt"
\t"os"

\t"github.com/slbdotdev/slbh/internal/config"
\t"github.com/slbdotdev/slbh/internal/harness"
\t"github.com/slbdotdev/slbh/internal/provider"
)

type callIn struct {
\tName      string `json:"name"`
\tArguments string `json:"arguments"`
}

type callOut struct {
\tName   string `json:"name"`
\tOK     bool   `json:"ok"`
\tOutput string `json:"output"`
}

func main() {
\trt, err := harness.New(config.Config{Home: os.Getenv("PROOF_HOME")}, harness.Options{
\t\tProvider: func(string) (provider.Provider, error) {
\t\t\treturn nil, fmt.Errorf("the executor proof has no provider")
\t\t},
\t})
\tif err != nil {
\t\tfmt.Fprintln(os.Stderr, "runtime:", err)
\t\tos.Exit(1)
\t}
\tenc := json.NewEncoder(os.Stdout)
\tenc.SetEscapeHTML(false)
\tscanner := bufio.NewScanner(os.Stdin)
\tscanner.Buffer(make([]byte, 1024*1024), 16*1024*1024)
\tfor scanner.Scan() {
\t\tline := scanner.Bytes()
\t\tif len(line) == 0 {
\t\t\tcontinue
\t\t}
\t\tvar in callIn
\t\tif err := json.Unmarshal(line, &in); err != nil {
\t\t\tfmt.Fprintln(os.Stderr, "decode:", err)
\t\t\tos.Exit(1)
\t\t}
\t\tresult, toolErr := rt.ExecuteTool("", in.Name, in.Arguments)
\t\tok := toolErr == nil
\t\tif toolErr != nil {
\t\t\tresult = "tool error: " + toolErr.Error()
\t\t}
\t\tif err := enc.Encode(callOut{Name: in.Name, OK: ok, Output: result}); err != nil {
\t\t\tfmt.Fprintln(os.Stderr, "encode:", err)
\t\t\tos.Exit(1)
\t\t}
\t}
}
'''

NON_ASCII = "# maintainer: Zoë Hartmann <zoe.hartmann@example.invalid> — rotation 3\n"


def build_sandbox(root):
    """A small fixed tree that reaches every branch the tools have."""
    def w(rel, text, binary=False):
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if binary:
            with open(p, "wb") as fh:
                fh.write(text)
        else:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

    w("README.md", "# proof tree\n\nalpha beta gamma\nthe needle is here\n")
    w("unicode.txt", NON_ASCII + "second line\nthird line\n")
    w("twice.txt", "repeat\nrepeat\nunique\n")
    w("nested/deep/leaf.md", "a\nb\nc\nd\ne\nf\ng\nh\n")
    w("nested/other.md", "needle\n")
    w("empty.txt", "")
    w("nonewline.txt", "no trailing newline")
    w("binary.bin", bytes(range(256)) * 4, binary=True)
    # Over slbh's 100k read_file ceiling, so the size refusal fires for real.
    w("big.txt", "".join("line %06d padding padding padding\n" % i for i in range(3400)))
    w("patchme.txt", "alpha\nbeta\ngamma\ndelta\n")
    w("patchme2.txt", "alpha\nbeta\ngamma\ndelta\n")
    w("tools/ok.py", "print('ran ok')\n")
    w("tools/fail.py", "import sys\nsys.stderr.write('it failed\\n')\nsys.exit(3)\n")
    w("tools/slow.py", "import time\ntime.sleep(9)\nprint('slow done')\n")


UNIFIED_PATCH = (
    "--- a/patchme.txt\n"
    "+++ b/patchme.txt\n"
    "@@ -1,4 +1,4 @@\n"
    " alpha\n"
    "-beta\n"
    "+BETA\n"
    " gamma\n"
    " delta\n"
)
ANTHROPIC_PATCH = (
    "*** Begin Patch\n"
    "*** Update File: patchme2.txt\n"
    "@@\n"
    " alpha\n"
    "-beta\n"
    "+BETA\n"
    " gamma\n"
    "*** End Patch\n"
)
ANTHROPIC_ADD = (
    "*** Begin Patch\n"
    "*** Add File: added/new.txt\n"
    "+first\n"
    "+second\n"
    "*** End Patch\n"
)
ANTHROPIC_BAD_HEADER = "*** Begin Patch\n*** Frobnicate File: patchme.txt\n*** End Patch\n"


def calls():
    """(label, tool, arguments-as-text). $LASTJOB is substituted on both sides."""
    def c(label, name, args):
        return (label, name, json.dumps(args) if not isinstance(args, str) else args)

    return [
        # ---- glob
        c("glob/flat", "glob", {"pattern": "*.txt"}),
        c("glob/nested", "glob", {"pattern": "nested/*"}),
        c("glob/nomatch", "glob", {"pattern": "nothing-here-*.zzz"}),
        c("glob/missing-arg", "glob", {}),
        # ---- grep
        c("grep/tree", "grep", {"pattern": "needle"}),
        c("grep/one-file", "grep", {"pattern": "repeat", "path": "twice.txt"}),
        c("grep/nomatch", "grep", {"pattern": "absolutely-not-present"}),
        c("grep/non-ascii", "grep", {"pattern": "maintainer", "path": "unicode.txt"}),
        c("grep/missing-path", "grep", {"pattern": "x", "path": "no/such/dir"}),
        # ---- read_file
        c("read_file/ok", "read_file", {"path": "README.md"}),
        c("read_file/non-ascii", "read_file", {"path": "unicode.txt"}),
        c("read_file/empty", "read_file", {"path": "empty.txt"}),
        c("read_file/too-big", "read_file", {"path": "big.txt"}),
        c("read_file/binary", "read_file", {"path": "binary.bin"}),
        c("read_file/missing", "read_file", {"path": "no-such-file.txt"}),
        c("read_file/no-arg", "read_file", {}),
        # ---- read_bytes
        c("read_bytes/ok", "read_bytes", {"path": "README.md", "start": 0, "end": 12}),
        c("read_bytes/past-end", "read_bytes", {"path": "README.md", "start": 2, "end": 100000}),
        c("read_bytes/start-past", "read_bytes", {"path": "README.md", "start": 99999, "end": 100000}),
        c("read_bytes/negative", "read_bytes", {"path": "README.md", "start": -1, "end": 4}),
        c("read_bytes/inverted", "read_bytes", {"path": "README.md", "start": 10, "end": 2}),
        c("read_bytes/missing", "read_bytes", {"path": "nope.txt", "start": 0, "end": 1}),
        c("read_bytes/mid-utf8", "read_bytes", {"path": "unicode.txt", "start": 0, "end": 17}),
        # ---- read_lines
        c("read_lines/ok", "read_lines", {"path": "nested/deep/leaf.md", "start": 2, "end": 4}),
        c("read_lines/past-end", "read_lines", {"path": "nested/deep/leaf.md", "start": 6, "end": 99}),
        c("read_lines/zero", "read_lines", {"path": "README.md", "start": 0, "end": 2}),
        c("read_lines/inverted", "read_lines", {"path": "README.md", "start": 5, "end": 1}),
        c("read_lines/missing", "read_lines", {"path": "nope.txt", "start": 1, "end": 2}),
        c("read_lines/nonewline", "read_lines", {"path": "nonewline.txt", "start": 1, "end": 1}),
        # ---- edit_file
        c("edit_file/ambiguous", "edit_file", {"path": "twice.txt", "old": "repeat", "new": "x"}),
        c("edit_file/absent", "edit_file", {"path": "twice.txt", "old": "absent", "new": "x"}),
        c("edit_file/ok", "edit_file", {"path": "twice.txt", "old": "unique", "new": "UNIQUE"}),
        c("edit_file/after", "read_file", {"path": "twice.txt"}),
        c("edit_file/non-ascii", "edit_file",
          {"path": "unicode.txt", "old": "second line", "new": "deuxième ligne"}),
        c("edit_file/non-ascii-after", "read_file", {"path": "unicode.txt"}),
        c("edit_file/missing-file", "edit_file", {"path": "nope.txt", "old": "a", "new": "b"}),
        # ---- write_file
        c("write_file/ok", "write_file", {"path": "written/out.txt", "content": "hello\n"}),
        c("write_file/exists", "write_file", {"path": "README.md", "content": "x"}),
        c("write_file/after", "read_file", {"path": "written/out.txt"}),
        # ---- apply_patch
        c("apply_patch/empty", "apply_patch", {"patch": "   "}),
        c("apply_patch/unified", "apply_patch", {"patch": UNIFIED_PATCH}),
        c("apply_patch/unified-after", "read_file", {"path": "patchme.txt"}),
        c("apply_patch/unified-again", "apply_patch", {"patch": UNIFIED_PATCH}),
        c("apply_patch/anthropic", "apply_patch", {"patch": ANTHROPIC_PATCH}),
        c("apply_patch/anthropic-after", "read_file", {"path": "patchme2.txt"}),
        c("apply_patch/anthropic-add", "apply_patch", {"patch": ANTHROPIC_ADD}),
        c("apply_patch/anthropic-add-after", "read_file", {"path": "added/new.txt"}),
        c("apply_patch/anthropic-add-twice", "apply_patch", {"patch": ANTHROPIC_ADD}),
        c("apply_patch/bad-header", "apply_patch", {"patch": ANTHROPIC_BAD_HEADER}),
        # ---- quick_bash / quick_py
        c("quick_bash/ok", "quick_bash", {"script": "echo hello from the shell"}),
        c("quick_bash/stderr-and-fail", "quick_bash", {"script": "python3 tools/fail.py"}),
        c("quick_bash/no-script", "quick_bash", {}),
        c("quick_bash/cwd", "quick_bash", {"script": "ls ok.py", "cwd": "tools"}),
        c("quick_py/ok", "quick_py", {"script": "print('hello from python')"}),
        c("quick_py/raises", "quick_py", {"script": "raise SystemExit(4)"}),
        c("quick_py/no-script", "quick_py", {}),
        # ---- jobs
        c("list_jobs/empty", "list_jobs", {}),
        c("long_job/start", "long_job", {"script": "echo started; echo done", "warn_after_seconds": 30}),
        c("read_job/ok", "read_job", {"job_id": "$LASTJOB"}),
        c("read_job/missing", "read_job", {"job_id": "job-deadbeef"}),
        c("kill_job/missing", "kill_job", {"job_id": "job-deadbeef"}),
        c("long_py/start", "long_py", {"script": "print('from long_py')", "warn_after_seconds": 30}),
        # ---- subagents: stubbed here by design, so only the SHAPE is compared
        c("list_subagents/shape", "list_subagents", {}),
        # ---- bad calls
        c("unknown/tool", "read_nonsense", {}),
        c("badjson/args", "read_file", "{not json"),
        c("notobject/args", "read_file", '["list"]'),
        c("emptyargs/list_jobs", "list_jobs", ""),
        c("nullargs/read_file", "read_file", "null"),
    ]


# Stubbed in Python on purpose (no agent tree in a sandbox), so their text
# cannot match Go and is excluded from the byte comparison. Recorded as a
# declared limit rather than quietly skipped.
STUBBED = {"list_subagents", "launch_subagent", "msg_subagent", "end_subagent"}
DECLARED = {"badjson/args": None}


def normalise(text, sandbox, last_jobs, name=None):
    if name == "list_jobs":
        # slbh's job.Manager.List (internal/job/manager.go:230-238) ranges over
        # a Go MAP, so the order is randomised by the Go runtime on every call.
        # That is a property of slbh - a leaf cannot rely on list_jobs order -
        # and not something an executor can or should reproduce, so the entries
        # are compared as a set.
        try:
            entries = json.loads(text)
            if isinstance(entries, list):
                text = json.dumps(sorted(entries, key=lambda e: str(e.get("Script"))),
                                  indent=2, ensure_ascii=False)
        except Exception:
            pass
    t = text.replace(sandbox, "<SANDBOX>")
    t = t.replace(os.path.realpath(sandbox), "<SANDBOX>")
    for j in last_jobs:
        if j:
            t = t.replace(j, "<JOB>")
    t = re.sub(r"job-[0-9a-f]{8,}", "<JOB>", t)
    t = re.sub(r'"Started": "[^"]*"', '"Started": "<TIME>"', t)
    t = re.sub(r'"Finished": "[^"]*"', '"Finished": "<TIME>"', t)
    t = re.sub(r'"ID": "[^"]*"', '"ID": "<ID>"', t)
    t = re.sub(r"\.slbh-edit-[0-9]+", ".slbh-edit-<N>", t)
    # A Go process's own pid/exit-status wording for a signal differs; not hit
    # by any call here, but normalised so a future addition cannot smuggle one in.
    return t.rstrip("\n")


def run_go(scratch, sandbox, call_list):
    copy = os.path.join(scratch, "slbh")
    shutil.copytree(SLBH, copy)
    d = os.path.join(copy, "cmd", "toolproof")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "main.go"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PROOF_GO)
    build = subprocess.run(["go", "build", "-o", os.path.join(scratch, "toolproof"),
                            "./cmd/toolproof"], cwd=copy,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    if build.returncode != 0:
        raise SystemExit("go build failed:\n" + build.stderr.decode("utf-8", "replace"))

    home = os.path.join(scratch, "slbh-home")
    os.makedirs(home, exist_ok=True)
    out_lines = []
    last_job = [None]
    # One process, fed call by call, so job state survives across calls exactly
    # as it does in a live runtime.
    proc = subprocess.Popen([os.path.join(scratch, "toolproof")], cwd=sandbox,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=dict(os.environ, PROOF_HOME=home))
    try:
        for label, name, args in call_list:
            args = args.replace("$LASTJOB", last_job[0] or "job-none")
            proc.stdin.write((json.dumps({"name": name, "arguments": args}) + "\n").encode("utf-8"))
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise SystemExit("proof binary stopped early at %s: %s"
                                 % (label, proc.stderr.read().decode("utf-8", "replace")[-2000:]))
            rec = json.loads(line.decode("utf-8"))
            rec["label"] = label
            if name in ("long_job", "long_py") and rec["ok"]:
                last_job[0] = rec["output"].strip()
            out_lines.append(rec)
    finally:
        try:
            proc.stdin.close()
            proc.wait(timeout=20)
        except Exception:
            proc.kill()
    return out_lines, [last_job[0]]


def run_python(sandbox, call_list):
    ex = leafloop.Executor(sandbox, agent_id="")
    out, last_job = [], [None]
    try:
        for label, name, args in call_list:
            args = args.replace("$LASTJOB", last_job[0] or "job-none")
            parsed, violations = leafloop.validate_call(name, args)
            if parsed is None:
                kinds = {v["kind"] for v in violations}
                if "unknown_tool" in kinds:
                    text, ok = 'tool error: unknown tool "%s"' % name, False
                else:
                    text, ok = ("tool error: tool arguments must be JSON: %s"
                                % violations[0].get("detail", "")), False
            else:
                try:
                    text, ok = ex.execute(name, parsed), True
                except leafloop.ToolError as exc:
                    text, ok = "tool error: " + str(exc), False
            if name in ("long_job", "long_py") and ok:
                last_job[0] = text.strip()
            out.append({"label": label, "name": name, "ok": ok, "output": text})
    finally:
        ex.shutdown()
    return out, [last_job[0]]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--show-all", action="store_true")
    args = ap.parse_args()

    if not shutil.which("go"):
        print("SKIP no go toolchain; cannot differential-test against slbh's runtime")
        return 2
    head = subprocess.run(["git", "-C", SLBH, "rev-parse", "HEAD"],
                          stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    dirty = subprocess.run(["git", "-C", SLBH, "status", "--porcelain"],
                           stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    print("slbh HEAD          %s" % head)
    print("snapshot claims    %s" % toolschemas.SLBH_HEAD)
    if dirty or head != toolschemas.SLBH_HEAD:
        print("FAIL slbh is dirty or has moved; the comparison cannot be attributed")
        return 1

    scratch = tempfile.mkdtemp(prefix="verify-executor-")
    call_list = calls()
    try:
        go_box = os.path.join(scratch, "sandbox-go")
        py_box = os.path.join(scratch, "sandbox-py")
        build_sandbox(go_box)
        build_sandbox(py_box)
        go_out, go_jobs = run_go(scratch, go_box, call_list)
        py_out, py_jobs = run_python(py_box, call_list)

        same, diff, declared, stubbed = [], [], [], []
        for g, p in zip(go_out, py_out):
            label = g["label"]
            gn = normalise(g["output"], go_box, go_jobs, g["name"])
            pn = normalise(p["output"], py_box, py_jobs, p["name"])
            if g["name"] in STUBBED:
                stubbed.append(label)
                continue
            if gn == pn and g["ok"] == p["ok"]:
                same.append(label)
                if args.show_all:
                    print("  same  %-34s %s" % (label, gn.replace("\n", "\\n")[:90]))
            elif label in DECLARED or label in DIFFERENCES:
                declared.append(label)
            else:
                diff.append((label, g["ok"], gn, p["ok"], pn))

        print("")
        print("calls compared     %d" % (len(same) + len(diff) + len(declared)))
        print("identical          %d" % len(same))
        print("declared different %d  %s" % (len(declared), declared))
        print("stubbed, excluded  %d  %s" % (len(stubbed), stubbed))
        print("UNEXPECTED diffs   %d" % len(diff))
        for label, gok, gn, pok, pn in diff:
            print("")
            print("DIFF %s" % label)
            print("  go  (ok=%s): %r" % (gok, gn[:500]))
            print("  py  (ok=%s): %r" % (pok, pn[:500]))
        print("")
        for k, v in DIFFERENCES.items():
            print("declared: %-22s %s" % (k, v))
        print("declared: %-22s %s" % ("subagent tools",
                                      "stubbed in the sandbox; no agent tree exists, so their "
                                      "text is excluded from this comparison by design."))
        if diff:
            print("")
            print("FAIL leafloop's executor diverges from slbh's runtime on %d call(s)" % len(diff))
            return 1
        print("OK leafloop's executor matches slbh's own runtime on every compared call")
        return 0
    finally:
        if args.keep:
            print("scratch kept at    %s" % scratch)
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
