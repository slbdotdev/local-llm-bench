#!/usr/bin/env python3
"""Prove toolschemas.py is a verbatim lift, by asking slbh's own Go to emit the same JSON.

    python3 verify_schemas.py            # compare, print the verdict
    python3 verify_schemas.py --keep     # leave the scratch build for inspection

slbh's tool definitions live in an `internal/` package, so they cannot be
imported from outside the module. This script therefore copies the slbh working
tree to a scratch directory, drops a `cmd/schemaproof` into the COPY, runs it,
and diffs the result against `toolschemas.openai_tools()`. /home/slb/slbh is
read only to this script and is never written to.

It also refuses to compare against a dirty working tree: if `git status
--porcelain` is non-empty, the tree is not the commit the snapshot claims and
the comparison would be attributed to the wrong HEAD.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toolschemas  # noqa: E402

SLBH = os.environ.get("SLBH_REPO", "/home/slb/slbh")

PROOF = '''// Scratch only. Emits slbh's leaf tool schemas in the OpenAI-compatible wire
// shape, by calling slbh's own harness.ToolDefinitions() and applying
// internal/provider/provider.go's own Request -> wire conversion
// (wireTool / wireToolFunction, provider.go:81-90 and 359-371).
package main

import (
\t"encoding/json"
\t"fmt"
\t"os"

\t"github.com/slbdotdev/slbh/internal/harness"
)

type wireToolFunction struct {
\tName        string         `json:"name"`
\tDescription string         `json:"description"`
\tParameters  map[string]any `json:"parameters"`
}

type wireTool struct {
\tType     string           `json:"type"`
\tFunction wireToolFunction `json:"function"`
}

func main() {
\ttools := harness.ToolDefinitions()
\tout := make([]wireTool, 0, len(tools))
\tfor _, t := range tools {
\t\tout = append(out, wireTool{Type: "function", Function: wireToolFunction{
\t\t\tName: t.Name, Description: t.Description, Parameters: t.Parameters,
\t\t}})
\t}
\tenc := json.NewEncoder(os.Stdout)
\tenc.SetIndent("", "  ")
\tenc.SetEscapeHTML(false)
\tif err := enc.Encode(out); err != nil {
\t\tfmt.Fprintln(os.Stderr, err)
\t\tos.Exit(1)
\t}
}
'''


def canonical(obj):
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    if not shutil.which("go"):
        print("SKIP no go toolchain; cannot verify against slbh's source")
        return 2
    if not os.path.isdir(SLBH):
        # This verifier needs slbh's own source and the Go toolchain, so it is
        # a Linux-side, dev-box-side check. On a clone that has only the
        # repository - the desktop D: checkout phase 2 grades from - there is
        # nothing to compare against and that is not a failure. Set SLBH_REPO
        # to point at a checkout elsewhere. `refprobe.py` is the probe that
        # runs everywhere.
        print("SKIP no slbh checkout at %s (set SLBH_REPO to override)" % SLBH)
        return 2
    head = subprocess.run(["git", "-C", SLBH, "rev-parse", "HEAD"],
                          stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    dirty = subprocess.run(["git", "-C", SLBH, "status", "--porcelain"],
                           stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    print("slbh HEAD            %s" % head)
    print("snapshot claims      %s" % toolschemas.SLBH_HEAD)
    print("working tree clean   %s" % (not dirty))
    if dirty:
        print("FAIL the slbh working tree is dirty; the comparison cannot be attributed")
        return 1
    if head != toolschemas.SLBH_HEAD:
        print("FAIL slbh has moved since the snapshot. Re-lift toolschemas.py and "
              "update SLBH_HEAD, then re-run every gate: the schemas are part of the "
              "instrument, not a detail.")
        return 1

    scratch = tempfile.mkdtemp(prefix="verify-schemas-")
    copy = os.path.join(scratch, "slbh")
    try:
        shutil.copytree(SLBH, copy)
        d = os.path.join(copy, "cmd", "schemaproof")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "main.go"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(PROOF)
        proc = subprocess.run(["go", "run", "./cmd/schemaproof"], cwd=copy,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        if proc.returncode != 0:
            print("FAIL go run: %s" % proc.stderr.decode("utf-8", "replace")[-2000:])
            return 1
        from_go = json.loads(proc.stdout.decode("utf-8"))
    finally:
        if args.keep:
            print("scratch kept at     %s" % scratch)
        else:
            shutil.rmtree(scratch, ignore_errors=True)

    from_py = toolschemas.openai_tools()
    names_go = [t["function"]["name"] for t in from_go]
    names_py = [t["function"]["name"] for t in from_py]
    print("tools from Go        %d" % len(from_go))
    print("tools from Python    %d" % len(from_py))
    print("order identical      %s" % (names_go == names_py))
    print("deep equal           %s" % (from_go == from_py))
    print("canonical sha256     %s" % canonical(from_go))
    print("toolschemas sha256   %s" % toolschemas.fingerprint())
    ok = from_go == from_py and canonical(from_go) == toolschemas.fingerprint()
    if not ok:
        for g, p in zip(from_go, from_py):
            if g != p:
                print("DIFF %s" % g["function"]["name"])
                print("  go: %s" % json.dumps(g, sort_keys=True)[:600])
                print("  py: %s" % json.dumps(p, sort_keys=True)[:600])
        missing = set(names_go) ^ set(names_py)
        if missing:
            print("NAME MISMATCH %s" % sorted(missing))
        print("FAIL toolschemas.py is not a verbatim lift")
        return 1
    print("OK toolschemas.py is byte-identical to what slbh's own Go emits, in slbh's order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
