#!/usr/bin/env python3
"""slbh's leaf tool schemas, lifted verbatim from slbh's own Go source.

PROVENANCE - this is a snapshot and must stay attributable
-----------------------------------------------------------
Source repository : /home/slb/slbh
git HEAD read     : bf858c6cbebe5f21216dbb2b1d071898489daf09
Read on           : 2026-09-11 (v8 phase 0, item 1)
Definition        : internal/harness/tools.go, func ToolDefinitions(), lines 24-57
Wire encoding     : internal/provider/provider.go
                      type wireTool / wireToolFunction, lines 81-90
                      Request -> wire conversion, lines 359-371
                      (each tool becomes {"type":"function","function":{name,description,parameters}})

Every tool below carries the tools.go line it came from. The name, the
description string and the parameters object are copied character for
character; nothing is paraphrased, reordered or "improved". ORDER IS
LOAD-BEARING and is slbh's order, not the order the v8 plan lists the tools
in: tools.go's own comment says "Keep ordering stable: provider prefix caching
keys include this schema."

WHAT A LEAF ACTUALLY GETS
-------------------------
All nineteen. internal/harness/agent.go:285 calls `tools := ToolDefinitions()`
unconditionally inside the agent turn loop, with no filtering by depth, model,
harness or parentage; `Agent.Depth` (agent.go:36) is used only for the
depth-two launch limit (runtime.go:305) and for the system prompt, never to
trim the tool list. So a depth-2 leaf is offered exactly the same nineteen
schemas as the root agent, including the four subagent tools it cannot
usefully call. That is a property of slbh worth measuring, not a bug in this
file.

TWO FACTS THE RUNNER AND THE GRADER BOTH DEPEND ON
--------------------------------------------------
1. A tool error replaces the tool result. agent.go:418-423:

       result, toolErr := a.runtime.ExecuteTool(...)
       if toolErr != nil { result = "tool error: " + toolErr.Error() }

   so when quick_bash exits non-zero, slbh's own quickBash returns
   stdout+stderr AND a non-nil error (tools.go:635-637) and the model is shown
   only `tool error: exit status 1` - the output is discarded. leafloop.py
   reproduces this exactly, because a model that cannot see a failing
   command's output is the thing being measured.
2. An unparseable or unknown call is also just a tool message:
   `tool arguments must be JSON: ...` (tools.go:67) or
   `unknown tool "x"` (tools.go:175). slbh never crashes the turn on one.

SCOPE
-----
This measures slbh's tool *surface*, not slbh's *runtime*. The schemas are
slbh's; the executor in leafloop.py is a Python re-implementation of
tools.go's semantics, and the four subagent tools are deliberately stubbed
(see leafloop.py). Any result produced with this file must say so.
"""

import hashlib
import json

# slbh tools.go:25-27 - the helper every single-string-argument tool uses.
#
#   stringArg := func(name string) map[string]any {
#       return map[string]any{"type": "object", "properties": map[string]any{name: map[string]any{"type": "string"}}, "required": []string{name}}
#   }


def _string_arg(name):
    return {"type": "object", "properties": {name: {"type": "string"}}, "required": [name]}


# slbh tools.go:28-56 - the returned []provider.Tool, in source order.
SLBH_TOOLS = [
    # tools.go:29
    {
        "name": "glob",
        "description": "Find files by a glob pattern.",
        "parameters": _string_arg("pattern"),
    },
    # tools.go:30
    {
        "name": "grep",
        "description": "Search text using a regular expression.",
        "parameters": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
            "required": ["pattern"],
        },
    },
    # tools.go:31
    {
        "name": "read_file",
        "description": "Read a whole file up to 100k bytes.",
        "parameters": _string_arg("path"),
    },
    # tools.go:32
    {
        "name": "read_bytes",
        "description": "Read an inclusive byte range from a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
            },
            "required": ["path", "start", "end"],
        },
    },
    # tools.go:33
    {
        "name": "read_lines",
        "description": "Read an inclusive line range from a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
            },
            "required": ["path", "start", "end"],
        },
    },
    # tools.go:34
    {
        "name": "edit_file",
        "description": "Replace an exact string in a file atomically.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old": {"type": "string"},
                "new": {"type": "string"},
            },
            "required": ["path", "old", "new"],
        },
    },
    # tools.go:35
    {
        "name": "apply_patch",
        "description": "Apply a unified patch to the working tree.",
        "parameters": _string_arg("patch"),
    },
    # tools.go:36
    {
        "name": "write_file",
        "description": "Create a new file; refuse to overwrite an existing file.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    # tools.go:37
    {
        "name": "quick_bash",
        "description": "Run a foreground shell command with a five second timeout.",
        "parameters": {
            "type": "object",
            "properties": {"script": {"type": "string"}, "cwd": {"type": "string"}},
            "required": ["script"],
        },
    },
    # tools.go:38
    {
        "name": "long_job",
        "description": "Start a non-blocking background shell job.",
        "parameters": {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "cwd": {"type": "string"},
                "warn_after_seconds": {"type": "integer"},
            },
            "required": ["script"],
        },
    },
    # tools.go:39
    {
        "name": "quick_py",
        "description": "Run Python code with the managed scientific environment and a five second timeout.",
        "parameters": {
            "type": "object",
            "properties": {"script": {"type": "string"}, "cwd": {"type": "string"}},
            "required": ["script"],
        },
    },
    # tools.go:40
    {
        "name": "long_py",
        "description": "Start a non-blocking background Python job in the managed scientific environment.",
        "parameters": {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "cwd": {"type": "string"},
                "warn_after_seconds": {"type": "integer"},
            },
            "required": ["script"],
        },
    },
    # tools.go:41
    {
        "name": "list_jobs",
        "description": "List all jobs in this runtime.",
        "parameters": {"type": "object", "properties": {}},
    },
    # tools.go:42
    {
        "name": "read_job",
        "description": "Read current stdout and stderr for a job.",
        "parameters": _string_arg("job_id"),
    },
    # tools.go:43
    {
        "name": "kill_job",
        "description": "Kill a job owned by the calling agent.",
        "parameters": _string_arg("job_id"),
    },
    # tools.go:44
    {
        "name": "list_subagents",
        "description": "List this runtime's agent tree.",
        "parameters": {"type": "object", "properties": {}},
    },
    # tools.go:45-53
    {
        "name": "launch_subagent",
        "description": (
            "Launch a child agent up to depth two; returns immediately. The parent chooses a "
            "relevant title made of three words joined by hyphens (for example "
            "inspect-api-cache); this is guidance only and is not enforced. Omit model for a "
            "native child to use its configured default. For a Codex leaf, set harness to codex "
            "and pass the exact ChatGPT model slug in model; Codex does not use the native "
            "approval list. Honor an explicit user model request. Do not wait or poll: results "
            "arrive as mandatory mid-turn steers at the next API/tool call boundary, or wake an "
            "idle parent. In-flight work finishes and its output is retained."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A relevant three-word dashed title chosen by the parent, such as inspect-api-cache. Guidance only; not enforced.",
                },
                "harness": {
                    "type": "string",
                    "enum": ["native", "codex"],
                    "description": "Harness for the child. Omit for native; use codex for a headless Codex ChatGPT leaf.",
                },
                "model": {
                    "type": "string",
                    "description": "Model ID. For harness codex, pass the exact ChatGPT model slug (for example gpt-5.6-luna); it may be any model available to the Codex account.",
                },
                "effort": {"type": "string"},
                "brief": {"type": "string"},
                "warn_after_seconds": {"type": "integer"},
                "working_dir": {"type": "string"},
            },
            "required": ["title", "brief"],
        },
    },
    # tools.go:54
    {
        "name": "msg_subagent",
        "description": (
            "Send a mandatory mid-turn steer to any agent in this runtime, including your parent "
            "or siblings. FIFO delivery at the next API/tool call boundary; wakes idle "
            "recipients. Never waits for turn completion or cancels in-flight work."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["agent_id", "message"],
        },
    },
    # tools.go:55
    {
        "name": "end_subagent",
        "description": "Stop a child agent.",
        "parameters": _string_arg("agent_id"),
    },
]

TOOL_NAMES = [t["name"] for t in SLBH_TOOLS]

# The four slbh tools that exist in a leaf's schema list but have no runtime
# behind them in this sandbox. leafloop.py answers them with a deterministic
# `tool error:` message and grade_loop.py counts a call to one of them as a
# wrong-tool call for every item 1 task.
UNAVAILABLE_IN_SANDBOX = ("list_subagents", "launch_subagent", "msg_subagent", "end_subagent")


def openai_tools():
    """slbh's tools in the OpenAI-compatible `tools` array shape.

    Mirrors provider.go:359-371 exactly: type "function", and a function
    object carrying name, description and parameters unchanged.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        }
        for t in SLBH_TOOLS
    ]


def schema_for(name):
    for t in SLBH_TOOLS:
        if t["name"] == name:
            return t["parameters"]
    return None


def fingerprint():
    """Stable sha256 over the emitted tools array.

    Recorded in every transcript header so a trial can be tied back to the
    exact schema snapshot it ran against, and so a later slbh change is
    detected rather than silently absorbed.
    """
    blob = json.dumps(openai_tools(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


SLBH_HEAD = "bf858c6cbebe5f21216dbb2b1d071898489daf09"
SLBH_SOURCE = "internal/harness/tools.go:24-57 (ToolDefinitions)"


def main():
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fingerprint", action="store_true", help="print the sha256 and exit")
    ap.add_argument("--names", action="store_true", help="print tool names, one per line, and exit")
    args = ap.parse_args()
    if args.fingerprint:
        print(fingerprint())
        return
    if args.names:
        for n in TOOL_NAMES:
            print(n)
        return
    print(json.dumps(openai_tools(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
