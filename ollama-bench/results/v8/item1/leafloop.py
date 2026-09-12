#!/usr/bin/env python3
"""leafloop - a thin leaf-agent loop over slbh's tool surface.

v8 item 1. POSTs to an OpenAI-compatible /v1/chat/completions endpoint with
slbh's nineteen leaf tool schemas (toolschemas.py, lifted verbatim from slbh
at bf858c6), executes every returned tool call inside a per-trial sandbox
directory, and appends every request, response, tool call and tool result to a
per-trial JSONL transcript. grade_loop.py reads only that transcript plus the
sandbox.

    # offline, no endpoint touched, no GPU:
    python3 leafloop.py --task tasks/t1-locate-report \
        --sandbox /tmp/trial1 --transcript /tmp/trial1.jsonl \
        --replay gates/fixtures/t1-locate-report/reference.jsonl

    # on the GPU (phase 2 only):
    python3 leafloop.py --task tasks/t1-locate-report \
        --endpoint http://fractal.wyvern-temperature.ts.net:11434 \
        --model local/q27-IQ2_M-96k --num-ctx 98304 \
        --sandbox /tmp/trial1 --transcript /tmp/trial1.jsonl

WHAT THIS IS AND IS NOT
-----------------------
It measures slbh's tool *surface* - the nineteen schemas, their descriptions,
their argument shapes and their error strings - driven from Python. It is not
slbh's runtime. The executor below is a Python re-implementation of
internal/harness/tools.go's semantics, faithful on the points a model can
observe, and the four subagent tools are stubbed because a sandbox has no
agent tree. Where fidelity is approximate it is marked `FIDELITY:`.

The one behaviour that is reproduced exactly because everything else depends
on it: slbh replaces a tool's output with its error (agent.go:418-421), so a
failing quick_bash shows the model `tool error: exit status 1` and *not* the
command's output.

STOP REASONS (never a crash)
----------------------------
    done              assistant returned a message with no tool calls
    turn_cap          --max-turns reached
    wall_cap          --wall-s reached
    replay_exhausted  --replay ran out of canned responses
    api_error         the endpoint failed after --retries attempts
    loop_error        an internal error; recorded, with the traceback

CAPS
----
--wall-s defaults to 900 s, the plan's longest pass@deadline rung. --max-turns
defaults to 40; slbh's own per-agent limit is 100 rounds (agent.go:291) and
--max-turns 100 reproduces it.
"""

import argparse
import glob as globmod
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toolschemas  # noqa: E402

# slbh internal/harness/agent.go:654, systemPrompt(), with its four %s slots
# filled for a depth-2 leaf in this runner. Kept verbatim otherwise, because
# this prompt is a large part of what decides whether a leaf calls a tool or
# narrates; ModelGuidance() is empty here (no /models approval list exists).
SYSTEM_PROMPT_TEMPLATE = (
    "You are %(title)s, an agent in slbh runtime %(runtime)s. Runtime depth is %(depth)d. "
    "Show reasoning and tool activity as events. Keep answers actionable and concise. "
    "Delegated work is asynchronous: launch_subagent returns immediately, so do not block this "
    "turn waiting for a child. Do not use quick_bash, long_job, sleep, polling, or shell wait "
    "loops to watch a child. Continue useful independent work if there is any; otherwise end "
    "your turn. Every message, including every [result from ...] message and completed long_job "
    "output, is a mandatory mid-turn steer: read and act on it during your current work. "
    "Messages enter context in FIFO order at the next API/tool call boundary; idle agents wake "
    "immediately. In-flight API and tool calls finish normally. Preserve all inference output "
    "and tool results; already-produced tool calls execute in order. Deferring a message until "
    "the end of a turn is a failure, never a delivery mode. Use msg_subagent to message any "
    "agent by ID, including your parent or siblings. As a parent, choose each subagent's title: "
    "use three relevant words joined by hyphens, such as inspect-api-cache. This is guidance, "
    "not a validation rule. As a parent, you are responsible for ending each subagent with "
    "end_subagent when its task is fully complete; subagents stay alive indefinitely so they "
    "can receive follow-up work. "
)

MAX_TOOL_RESULT_CHARS = 120000  # a read_file of a 100k file plus slack; slbh has no cap


# --------------------------------------------------------------------------
# transcript
# --------------------------------------------------------------------------
class Transcript:
    def __init__(self, path):
        self.path = path
        d = os.path.dirname(os.path.abspath(path))
        if d:
            os.makedirs(d, exist_ok=True)
        self.fh = open(path, "w", encoding="utf-8", newline="\n")

    def write(self, rec, **fields):
        fields["rec"] = rec
        fields.setdefault("t", round(time.time(), 3))
        self.fh.write(json.dumps(fields, ensure_ascii=False, sort_keys=False) + "\n")
        self.fh.flush()

    def close(self):
        self.fh.close()


# --------------------------------------------------------------------------
# schema validation - against slbh's own lifted schemas, nothing invented
# --------------------------------------------------------------------------
_JSON_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}


def validate_call(name, raw_arguments):
    """Return (parsed_args_or_None, violations).

    Violation kinds, in the order slbh would hit them:
      unknown_tool        no such tool in ToolDefinitions()
      bad_json            arguments are not JSON (tools.go:67)
      not_object          arguments parsed to something other than an object
      missing_required    a `required` property absent
      wrong_type          a property present with the wrong JSON type
      bad_enum            a value outside an `enum`
      extra_property      a property the schema does not declare

    extra_property is reported but is NOT counted as a schema violation by
    grade_loop: slbh ignores unknown keys (tools.go:195-210 read only the keys
    it wants), so a checker stricter than slbh would manufacture a number.
    """
    violations = []
    schema = toolschemas.schema_for(name)
    if schema is None:
        return None, [{"kind": "unknown_tool", "detail": name}]
    text = raw_arguments if isinstance(raw_arguments, str) else json.dumps(raw_arguments)
    if text is None or text.strip() == "":
        parsed = {}  # tools.go:63-65 - empty arguments are an empty map, not an error
    else:
        try:
            parsed = json.loads(text)
        except Exception as exc:
            return None, [{"kind": "bad_json", "detail": str(exc)}]
    if parsed is None:
        # Go unmarshals `null` into a nil map with no error (tools.go:66); the
        # tool then sees every argument as absent.
        parsed = {}
    if not isinstance(parsed, dict):
        # encoding/json's own wording, reproduced because it is deterministic
        # and it is what the model reads back. Verified against slbh's runtime.
        go_kind = {list: "array", str: "string", bool: "bool"}.get(type(parsed), "number")
        return None, [{
            "kind": "not_object",
            "detail": "json: cannot unmarshal %s into Go value of type map[string]interface {}"
                      % go_kind,
        }]
    props = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in parsed:
            violations.append({"kind": "missing_required", "detail": key})
    for key, value in parsed.items():
        spec = props.get(key)
        if spec is None:
            violations.append({"kind": "extra_property", "detail": key})
            continue
        want = spec.get("type")
        py = _JSON_TYPES.get(want)
        if py is not None:
            # JSON has no int/float split the way Python does; an integer
            # arrives as float from some servers, and slbh's intValue
            # (tools.go:202-210) accepts float64 then truncates. Accept a
            # float that is integral, reject one that is not.
            ok = isinstance(value, py) and not (want != "boolean" and isinstance(value, bool))
            if want == "integer" and isinstance(value, float):
                ok = value.is_integer()
            if not ok:
                violations.append(
                    {"kind": "wrong_type", "detail": "%s: want %s, got %s" % (key, want, type(value).__name__)}
                )
                continue
        if "enum" in spec and value not in spec["enum"]:
            violations.append({"kind": "bad_enum", "detail": "%s=%r" % (key, value)})
    return parsed, violations


# --------------------------------------------------------------------------
# the executor - slbh internal/harness/tools.go semantics, in Python
# --------------------------------------------------------------------------
class ToolError(Exception):
    pass


class Job:
    def __init__(self, job_id, script, tool_name, warn_after_s, cwd, argv,
                 author="agent-item1leaf"):
        self.id = job_id
        self.author = author
        self.script = script
        self.tool_name = tool_name
        self.warn_after_s = warn_after_s
        self.started = time.time()
        self.finished = None
        self.out_path = tempfile.mkstemp(prefix="slbh-job-out-")[1]
        self.err_path = tempfile.mkstemp(prefix="slbh-job-err-")[1]
        self._out = open(self.out_path, "wb")
        self._err = open(self.err_path, "wb")
        self.killed = False
        self.proc = subprocess.Popen(argv, cwd=cwd, stdout=self._out, stderr=self._err)

    def poll(self):
        code = self.proc.poll()
        if code is not None and self.finished is None:
            self.finished = time.time()
            try:
                self._out.close()
                self._err.close()
            except Exception:
                pass
        return code

    @property
    def status(self):
        code = self.poll()
        if code is None:
            return "running"
        if self.killed:
            return "killed"
        return "complete" if code == 0 else "failed"

    def output(self):
        self.poll()
        out = open(self.out_path, "rb").read().decode("utf-8", "replace")
        err = open(self.err_path, "rb").read().decode("utf-8", "replace")
        return out, err

    def kill(self):
        if self.poll() is None:
            self.killed = True
            try:
                self.proc.kill()
            except Exception:
                pass
            try:
                self.proc.wait(timeout=5)
            except Exception:
                pass
        self.poll()

    def snapshot(self):
        # FIDELITY: mirrors Go job.Snapshot (internal/job/manager.go:36-48),
        # which has no json tags, so Go marshals the exported field names
        # as-is and a time.Duration as int64 nanoseconds. Reproduced so a
        # model sees the same keys it would see from slbh.
        out, err = self.output()
        code = self.poll()
        return {
            "ID": self.id,
            "Author": self.author,
            "Script": self.script,
            "ToolName": self.tool_name,
            "Status": self.status,
            "Started": _rfc3339(self.started),
            "Finished": _rfc3339(self.finished) if self.finished else "0001-01-01T00:00:00Z",
            "ExitCode": code if code is not None else 0,
            "StdoutBytes": len(out.encode("utf-8")),
            "StderrBytes": len(err.encode("utf-8")),
            "WarnAfter": int(self.warn_after_s * 1e9),
        }


def _rfc3339(ts):
    import datetime

    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )


def _short_id(prefix):
    return "%s-%s" % (prefix, os.urandom(4).hex())


class Executor:
    """slbh's Runtime.ExecuteTool, for one sandbox base directory."""

    def __init__(self, base, python_exe=None, shell=None, job_counter_start=0,
                 agent_id="agent-item1leaf"):
        self.base = os.path.abspath(base)
        self.agent_id = agent_id
        self.jobs = {}
        self.job_order = []
        self.python_exe = python_exe or _python_executable()
        self.shell = shell or _shell()
        self._deterministic_ids = os.environ.get("LEAFLOOP_DETERMINISTIC_IDS") == "1"
        self._job_n = job_counter_start

    # -- slbh tools.go:216-228 resolvePath
    def resolve(self, path):
        if path == "":
            raise ToolError("path is required")
        if not os.path.isabs(path):
            path = os.path.join(self.base, path)
        clean = os.path.abspath(path)
        return clean

    def _new_job_id(self):
        if self._deterministic_ids:
            self._job_n += 1
            return "job-%08d" % self._job_n
        return _short_id("job")

    def execute(self, name, args):
        fn = getattr(self, "_t_" + name, None)
        if fn is None:
            # tools.go:175
            raise ToolError('unknown tool "%s"' % name)
        return fn(args)

    # ---- read side ------------------------------------------------------
    def _t_glob(self, a):
        pattern = _s(a, "pattern")
        if pattern == "":
            raise ToolError("pattern is required")  # tools.go:232
        absolute = os.path.isabs(pattern)
        resolved = self.resolve(pattern)
        # FIDELITY: Go filepath.Glob has no `**`; Python's non-recursive glob
        # treats `**` as `*`, which is the same behaviour.
        matches = globmod.glob(resolved)
        if not absolute:
            matches = [os.path.relpath(m, self.base) for m in matches]
        matches.sort()
        return "\n".join(matches)

    def _t_grep(self, a):
        pattern = _s(a, "pattern")
        path = _s(a, "path", ".")
        try:
            # FIDELITY: Go regexp is RE2; Python re is a superset, so a
            # backreference or lookaround that slbh would reject compiles
            # here. grade_loop records the pattern so this is auditable.
            rx = re.compile(pattern)
        except Exception as exc:
            raise ToolError("error parsing regexp: %s" % exc)
        absolute = os.path.isabs(path)
        walk = self.resolve(path)
        if not os.path.exists(walk):
            # Go's filepath.Walk surfaces the lstat failure and slbh returns it
            # (tools.go:263-265, 292). Verified against slbh's own runtime by
            # verify_executor.py.
            raise ToolError("lstat %s: no such file or directory" % walk)
        out = []
        if os.path.isfile(walk):
            targets = [walk]
        else:
            targets = []
            for root, dirs, names in os.walk(walk):
                dirs.sort()
                for n in sorted(names):
                    targets.append(os.path.join(root, n))
        for f in targets:
            try:
                if os.path.getsize(f) > 2 * 1024 * 1024:  # tools.go:270
                    continue
                with open(f, "rb") as fh:
                    data = fh.read()
            except OSError:
                continue
            display = f if absolute else os.path.relpath(f, self.base)
            for i, line in enumerate(data.split(b"\n"), start=1):
                text = line.rstrip(b"\r").decode("utf-8", "replace")
                if rx.search(text):
                    out.append("%s:%d:%s" % (display, i, text))
        return "\n".join(out) + ("\n" if out else "")

    def _t_read_file(self, a):
        f = self.resolve(_s(a, "path"))
        if not os.path.exists(f):
            raise ToolError("stat %s: no such file or directory" % f)
        size = os.path.getsize(f)
        if size > 100 * 1024:  # tools.go:304-307
            data = open(f, "rb").read()
            raise ToolError(
                "file is %d bytes, %d lines, type %s; use read_lines or read_bytes instead"
                % (size, data.count(b"\n") + 1, _detect_type(f))
            )
        return open(f, "rb").read().decode("utf-8", "replace")

    def _t_read_bytes(self, a):
        start, end = _i(a, "start"), _i(a, "end")
        if start < 0 or end < start or end - start + 1 > 100 * 1024:  # tools.go:313
            raise ToolError("byte range must be zero-based, inclusive, and at most 100k bytes")
        f = self.resolve(_s(a, "path"))
        if not os.path.exists(f):
            raise ToolError("open %s: no such file or directory" % f)
        data = open(f, "rb").read()
        if start >= len(data):
            raise ToolError("byte start %d is past file size %d" % (start, len(data)))
        if end >= len(data):
            end = len(data) - 1
        return data[start : end + 1].decode("utf-8", "replace")

    def _t_read_lines(self, a):
        start, end = _i(a, "start"), _i(a, "end")
        if start < 1 or end < start:  # tools.go:345
            raise ToolError("line range must be one-based and inclusive")
        f = self.resolve(_s(a, "path"))
        if not os.path.exists(f):
            raise ToolError("open %s: no such file or directory" % f)
        out = []
        with open(f, "rb") as fh:
            for i, line in enumerate(fh, start=1):
                if i > end:
                    break
                if i >= start:
                    out.append(
                        "%d:%s" % (i, line.rstrip(b"\n").rstrip(b"\r").decode("utf-8", "replace"))
                    )
        return "\n".join(out) + ("\n" if out else "")

    # ---- write side -----------------------------------------------------
    def _t_edit_file(self, a):
        f = self.resolve(_s(a, "path"))
        if not os.path.exists(f):
            raise ToolError("open %s: no such file or directory" % f)
        raw = open(f, "rb").read()
        text = raw.decode("utf-8", "surrogateescape")
        old, new = _s(a, "old"), _s(a, "new")
        count = text.count(old) if old else 0
        if count != 1:  # tools.go:383-385
            raise ToolError("replacement matched %d locations; expected exactly one" % count)
        text = text.replace(old, new, 1)
        _atomic_replace(f, text.encode("utf-8", "surrogateescape"))
        return "updated"

    def _t_write_file(self, a):
        f = self.resolve(_s(a, "path"))
        if os.path.exists(f):  # tools.go:395-397
            raise ToolError("file already exists")
        os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
        with open(f, "xb") as fh:
            fh.write(_s(a, "content").encode("utf-8"))
        return "created"

    def _t_apply_patch(self, a):
        patch = _s(a, "patch")
        if patch.strip() == "":  # tools.go:453
            raise ToolError("patch is empty")
        if patch.strip().startswith("*** Begin Patch"):
            self._apply_anthropic_patch(patch)
            return "applied"
        proc = subprocess.run(
            ["git", "apply", "--unsafe-paths", "--whitespace=nowarn", "-"],
            cwd=self.base,
            input=patch.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:  # tools.go:467-469
            raise ToolError(
                "git apply: exit status %d: %s"
                % (proc.returncode, proc.stderr.decode("utf-8", "replace").strip())
            )
        return "applied"

    def _apply_anthropic_patch(self, patch):
        """slbh tools.go:473-587, applyAnthropicPatch, line for line."""
        lines = patch.replace("\r\n", "\n").split("\n")
        if len(lines) < 2 or lines[0].strip() != "*** Begin Patch":
            raise ToolError("patch must start with *** Begin Patch")
        i = 1
        while i < len(lines):
            if lines[i] == "" or lines[i] == "*** End Patch":
                i += 1
                continue
            header = lines[i]
            if header.startswith("*** Add File: "):
                path = header[len("*** Add File: ") :].strip()
                i += 1
                content = []
                while i < len(lines) and not lines[i].startswith("*** "):
                    if not lines[i].startswith("+"):
                        raise ToolError('add file "%s" contains a non-add line' % path)
                    content.append(lines[i][1:])
                    i += 1
                f = self.resolve(path)
                if os.path.exists(f):
                    raise ToolError('add file "%s" already exists' % path)
                os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
                with open(f, "wb") as fh:
                    fh.write("\n".join(content).encode("utf-8"))
                continue
            if header.startswith("*** Delete File: "):
                path = header[len("*** Delete File: ") :].strip()
                f = self.resolve(path)
                try:
                    os.remove(f)
                except OSError as exc:
                    raise ToolError('delete file "%s": %s' % (path, exc))
                i += 1
                continue
            if header.startswith("*** Update File: "):
                path = header[len("*** Update File: ") :].strip()
                f = self.resolve(path)
                if not os.path.exists(f):
                    raise ToolError("open %s: no such file or directory" % f)
                original = open(f, "rb").read().decode("utf-8", "surrogateescape")
                had_newline = original.endswith("\n")
                body = original[:-1] if had_newline else original
                file_lines = body.split("\n")
                if len(file_lines) == 1 and file_lines[0] == "" and not had_newline:
                    file_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("*** "):
                    if not lines[i].startswith("@@"):
                        i += 1
                        continue
                    i += 1
                    old_lines, new_lines = [], []
                    while (
                        i < len(lines)
                        and not lines[i].startswith("@@")
                        and not lines[i].startswith("*** ")
                    ):
                        line = lines[i]
                        if line == "":
                            old_lines.append("")
                            new_lines.append("")
                            i += 1
                            continue
                        c = line[0]
                        if c == " ":
                            old_lines.append(line[1:])
                            new_lines.append(line[1:])
                        elif c == "-":
                            old_lines.append(line[1:])
                        elif c == "+":
                            new_lines.append(line[1:])
                        else:
                            raise ToolError('invalid update line "%s"' % line)
                        i += 1
                    at = _find_lines(file_lines, old_lines)
                    if at < 0:
                        raise ToolError('hunk for "%s" did not match' % path)
                    file_lines = file_lines[:at] + new_lines + file_lines[at + len(old_lines) :]
                content = "\n".join(file_lines)
                if had_newline:
                    content += "\n"
                _atomic_replace(f, content.encode("utf-8", "surrogateescape"))
                continue
            raise ToolError('unknown patch header "%s"' % header)

    # ---- execution ------------------------------------------------------
    def _cwd_for(self, a):
        cwd = _s(a, "cwd", self.base)
        if cwd == "" or cwd == self.base:
            return self.base
        return self.resolve(cwd)

    def _t_quick_bash(self, a):
        script = _s(a, "script")
        if script == "":
            raise ToolError("script is required")
        return self._run_foreground(self.shell[0], self.shell[1](script), self._cwd_for(a), "quick_bash")

    def _t_quick_py(self, a):
        script = _s(a, "script")
        if script == "":
            raise ToolError("script is required")
        return self._run_foreground(
            self.python_exe, [self.python_exe, "-c", script], self._cwd_for(a), "quick_py"
        )

    def _run_foreground(self, exe, argv, cwd, label):
        try:
            proc = subprocess.run(
                argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5.0
            )
        except subprocess.TimeoutExpired:
            raise ToolError("%s timed out" % label)  # tools.go:632-634
        out = proc.stdout.decode("utf-8", "replace")
        err = proc.stderr.decode("utf-8", "replace")
        if proc.returncode != 0:
            # tools.go:635-637 returns (stdout+stderr, err) and agent.go:419-421
            # then THROWS THE OUTPUT AWAY and shows only the error. Reproduced
            # deliberately: a leaf that cannot see a failing command's output
            # is the thing under test.
            raise ToolError("exit status %d" % proc.returncode)
        return out

    def _t_long_job(self, a):
        script = _s(a, "script")
        if script == "":
            raise ToolError("script is required")
        warn = _i(a, "warn_after_seconds") or 5  # tools.go:101-104
        cwd = self._cwd_for(a)
        jid = self._new_job_id()
        job = Job(jid, script, "long_job", warn, cwd, self.shell[1](script),
                  author=self.agent_id)
        self.jobs[jid] = job
        self.job_order.append(jid)
        return jid

    def _t_long_py(self, a):
        script = _s(a, "script")
        if script == "":
            raise ToolError("script is required")
        warn = _i(a, "warn_after_seconds") or 5
        cwd = self._cwd_for(a)
        jid = self._new_job_id()
        job = Job(jid, script, "long_py", warn, cwd,
                  [self.python_exe, "-c", script], author=self.agent_id)
        self.jobs[jid] = job
        self.job_order.append(jid)
        return jid

    def _t_list_jobs(self, a):
        return _go_json([self.jobs[j].snapshot() for j in self.job_order])

    def _t_read_job(self, a):
        jid = _s(a, "job_id")
        job = self.jobs.get(jid)
        if job is None:
            raise ToolError("job not found")  # tools.go:135
        out, err = job.output()
        return _go_json({"stdout": out, "stderr": err}, sort_keys=True)

    def _t_kill_job(self, a):
        jid = _s(a, "job_id")
        job = self.jobs.get(jid)
        if job is None:
            # job.Manager.Kill quotes the id; tools.go's own read_job lookup
            # does not. Both wordings verified against slbh's runtime.
            raise ToolError('job "%s" not found' % jid)
        job.kill()
        return "killed"

    # ---- the four with no runtime in a sandbox --------------------------
    # Present in the schema list because slbh gives them to every leaf
    # (agent.go:285, no depth filter). A call to one is a real signal - the
    # leaf tried to delegate its own task - so it is answered, recorded, and
    # counted by grade_loop as a wrong-tool call.
    _SUBAGENT_STUB = (
        "this runtime has no agent tree: the item 1 runner measures slbh's tool surface, "
        "not slbh's runtime. Do the work yourself with the file, shell and job tools."
    )

    def _t_list_subagents(self, a):
        return _go_json(
            [
                {
                    "ID": "agent-item1leaf",
                    "Title": "item1-leaf-trial",
                    "ParentID": "",
                    "Depth": 2,
                    "Model": "under-test",
                    "Harness": "native",
                    "Status": "working",
                }
            ]
        )

    def _t_launch_subagent(self, a):
        raise ToolError(self._SUBAGENT_STUB)

    def _t_msg_subagent(self, a):
        raise ToolError(self._SUBAGENT_STUB)

    def _t_end_subagent(self, a):
        raise ToolError(self._SUBAGENT_STUB)

    def shutdown(self):
        for jid in self.job_order:
            try:
                self.jobs[jid].kill()
            except Exception:
                pass


def _s(a, key, default=""):
    v = a.get(key)
    return v if isinstance(v, str) else default  # tools.go:196-201


def _i(a, key):
    v = a.get(key)
    if isinstance(v, bool):
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    return 0  # tools.go:202-210


def _find_lines(haystack, needle):
    """slbh tools.go:589-610. -1 not found, -2 ambiguous, else index."""
    if not needle:
        return len(haystack)
    found = -1
    for i in range(0, len(haystack) - len(needle) + 1):
        if haystack[i : i + len(needle)] == needle:
            if found >= 0:
                return -2
            found = i
    return found


def _atomic_replace(path, data):
    """slbh tools.go:419-450 - temp file in the same directory, then rename."""
    d = os.path.dirname(path) or "."
    mode = 0o600
    try:
        mode = os.stat(path).st_mode & 0o777
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(prefix=".slbh-edit-", dir=d)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _detect_type(path):
    """Approximates Go net/http.DetectContentType for the cases a text corpus hits."""
    try:
        head = open(path, "rb").read(512)
    except OSError:
        return "unknown"
    if b"\x00" in head:
        return "application/octet-stream"
    try:
        head.decode("utf-8")
        return "text/plain; charset=utf-8"
    except UnicodeDecodeError:
        return "application/octet-stream"


def _go_json(value, sort_keys=False):
    """json.MarshalIndent(value, "", "  ") - tools.go:211-214.

    Go sorts the keys of a MAP and keeps the declared field order of a STRUCT.
    read_job marshals map[string]string, so it sorts; list_jobs marshals
    []job.Snapshot, so it does not. Both verified against slbh's own runtime.
    """
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=sort_keys)


def _python_executable():
    if os.environ.get("SLBH_PYTHON", "").strip():
        return os.environ["SLBH_PYTHON"].strip()
    venv = os.path.join(
        os.path.expanduser("~"), ".local", "share", "slbh", "python",
        "Scripts" if os.name == "nt" else "bin",
        "python.exe" if os.name == "nt" else "python",
    )
    if os.path.exists(venv):
        return venv
    return shutil.which("python3") or sys.executable


def _shell():
    """(name, argv_builder) mirroring slbh shell_linux.go / shell_other.go."""
    if os.name == "nt":
        return ("cmd.exe", lambda s: ["cmd.exe", "/d", "/c", s])
    if sys.platform.startswith("linux"):
        return ("bash", lambda s: ["bash", "-lc", s])
    return ("sh", lambda s: ["sh", "-c", s])


# --------------------------------------------------------------------------
# the model side
# --------------------------------------------------------------------------
class Replay:
    """Canned assistant responses, one per line, instead of an endpoint.

    Each line is any of:
        {"role":"assistant","content":...,"tool_calls":[...]}
        {"message":{...},"usage":{...}}
        {"choices":[{"message":{...}}],"usage":{...}}
    A tool call's "arguments" may be a JSON string (as the wire has it) or an
    object, which is serialised here; a fixture that wants to test bad JSON
    passes a string and it is used untouched.
    """

    def __init__(self, path):
        self.lines = []
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw or raw.startswith("//"):
                    continue
                self.lines.append(json.loads(raw))
        self.n = 0
        self.path = path

    def next(self):
        if self.n >= len(self.lines):
            return None
        rec = self.lines[self.n]
        self.n += 1
        if "choices" in rec:
            body = rec
        elif "message" in rec:
            body = {"choices": [{"message": rec["message"], "finish_reason": rec.get("finish_reason")}]}
            if "usage" in rec:
                body["usage"] = rec["usage"]
            for k in ("prompt_eval_count", "eval_count"):
                if k in rec:
                    body[k] = rec[k]
        else:
            body = {"choices": [{"message": rec}]}
        msg = body["choices"][0]["message"]
        for call in msg.get("tool_calls") or []:
            fn = call.get("function", {})
            if not isinstance(fn.get("arguments"), str):
                fn["arguments"] = json.dumps(fn.get("arguments", {}), ensure_ascii=False)
        return body


def post_json(url, payload, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_usage(body):
    """(prompt_tokens, output_tokens) from either wire shape.

    Ollama's native /api/chat reports prompt_eval_count / eval_count; its
    OpenAI-compatible /v1/chat/completions reports usage.prompt_tokens /
    usage.completion_tokens. The plan names prompt_eval_count, so that is
    preferred where present.
    """
    p = body.get("prompt_eval_count")
    o = body.get("eval_count")
    usage = body.get("usage") or {}
    if p is None:
        p = usage.get("prompt_tokens")
    if o is None:
        o = usage.get("completion_tokens")
    return p, o


def normalise_message(body):
    if "message" in body and "choices" not in body:
        return body["message"], body.get("done_reason")
    choice = (body.get("choices") or [{}])[0]
    return choice.get("message") or {}, choice.get("finish_reason")


# --------------------------------------------------------------------------
# the loop
# --------------------------------------------------------------------------
def prepare_sandbox(task_dir, sandbox):
    seed = os.path.join(task_dir, "seed")
    if os.path.exists(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(os.path.dirname(os.path.abspath(sandbox)) or ".", exist_ok=True)
    shutil.copytree(seed, sandbox)
    return sandbox


def sandbox_fingerprint(sandbox):
    """sha256 over (relpath, bytes) for every file, so the grader can prove
    which files a trial changed without trusting the model's account."""
    h = hashlib.sha256()
    per_file = {}
    for root, dirs, names in os.walk(sandbox):
        dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", ".git"))
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, sandbox).replace(os.sep, "/")
            data = open(p, "rb").read()
            fh = hashlib.sha256(data).hexdigest()
            per_file[rel] = fh
            h.update(rel.encode("utf-8") + b"\0" + fh.encode("ascii") + b"\0")
    return h.hexdigest(), per_file


class Injector:
    """One injected tool error, per the task's MANIFEST `inject_error`.

    Fields: tool (required), occurrence (1-based, default 1), path_contains
    (optional substring filter on any string argument), message (the text
    after `tool error: `). Fires once. When it never fires, the grader
    records recovery as `na` rather than guessing.
    """

    def __init__(self, spec):
        self.spec = spec or None
        self.seen = 0
        self.fired = False

    def should_fire(self, name, args):
        if not self.spec or self.fired or name != self.spec.get("tool"):
            return False
        needle = self.spec.get("path_contains")
        if needle:
            if not any(isinstance(v, str) and needle in v for v in (args or {}).values()):
                return False
        self.seen += 1
        if self.seen < int(self.spec.get("occurrence", 1)):
            return False
        self.fired = True
        return True

    def message(self):
        return self.spec.get("message", "injected tool error")


def run(args):
    task_dir = os.path.abspath(args.task)
    manifest_path = os.path.join(task_dir, "MANIFEST.json")
    manifest = {}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path, encoding="utf-8"))
    prompt = open(os.path.join(task_dir, "prompt.md"), encoding="utf-8").read()

    inject_spec = manifest.get("inject_error")
    if args.inject_error:
        inject_spec = json.loads(args.inject_error)
    if args.no_inject:
        inject_spec = None
    injector = Injector(inject_spec)

    sandbox = prepare_sandbox(task_dir, os.path.abspath(args.sandbox))
    before_hash, before_files = sandbox_fingerprint(sandbox)

    tx = Transcript(args.transcript)
    executor = Executor(sandbox)
    tools = toolschemas.openai_tools()
    system = SYSTEM_PROMPT_TEMPLATE % {
        "title": args.agent_title,
        "runtime": args.runtime_id,
        "depth": args.depth,
    }

    replay = Replay(args.replay) if args.replay else None
    url = None
    if replay is None:
        base = args.endpoint.rstrip("/")
        url = base + ("/api/chat" if args.api == "native" else "/v1/chat/completions")

    tx.write(
        "header",
        harness_version="v8-item1",
        task=os.path.basename(task_dir),
        task_dir=task_dir,
        model=args.model,
        endpoint=args.endpoint if replay is None else None,
        api=args.api if replay is None else "replay",
        replay=args.replay,
        num_ctx=args.num_ctx,
        temperature=args.temperature,
        max_turns=args.max_turns,
        wall_s_cap=args.wall_s,
        sandbox=sandbox,
        slbh_head=toolschemas.SLBH_HEAD,
        slbh_source=toolschemas.SLBH_SOURCE,
        tools_sha256=toolschemas.fingerprint(),
        tool_names=toolschemas.TOOL_NAMES,
        inject_error=inject_spec,
        sandbox_sha256_before=before_hash,
        system_prompt=system,
        prompt=prompt,
        started_at=time.time(),
    )

    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    t0 = time.time()
    stop_reason = None
    turns = 0
    prompt_tokens_total = 0
    output_tokens_total = 0
    peak_prompt = 0
    last_prompt_tokens = None
    api_calls = 0
    traceback_text = None

    try:
        while True:
            elapsed = time.time() - t0
            if elapsed >= args.wall_s:
                stop_reason = "wall_cap"
                break
            if turns >= args.max_turns:
                stop_reason = "turn_cap"
                break

            payload = {
                "model": args.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
            }
            if args.temperature is not None:
                payload["temperature"] = args.temperature
            if args.num_ctx:
                # Native /api/chat honours options.num_ctx. The OpenAI-compat
                # path ignores unknown keys, so it is sent for the record and
                # the live tag (q27-IQ2_M-96k) carries the window itself. The
                # num_ctx that was actually in force is proved by peak_prompt
                # plus /api/show at round time, never by this field.
                payload["options"] = {"num_ctx": args.num_ctx}
            tx.write("request", turn=turns, payload=payload, elapsed_s=round(elapsed, 3))

            call_t0 = time.time()
            if replay is not None:
                body = replay.next()
                if body is None:
                    stop_reason = "replay_exhausted"
                    break
                err = None
            else:
                body, err = None, None
                remaining = max(1.0, args.wall_s - (time.time() - t0))
                for attempt in range(args.retries + 1):
                    try:
                        body = post_json(url, payload, timeout=min(remaining, args.http_timeout))
                        break
                    except Exception as exc:  # noqa: BLE001
                        err = "%s: %s" % (type(exc).__name__, exc)
                        tx.write("api_retry", turn=turns, attempt=attempt, error=err)
                        if time.time() - t0 >= args.wall_s:
                            break
                if body is None:
                    tx.write("api_error", turn=turns, error=err)
                    stop_reason = "api_error"
                    break
            api_calls += 1
            call_wall = time.time() - call_t0

            p_tok, o_tok = extract_usage(body)
            if p_tok:
                prompt_tokens_total += p_tok
                peak_prompt = max(peak_prompt, p_tok)
                last_prompt_tokens = p_tok
            if o_tok:
                output_tokens_total += o_tok
            message, finish_reason = normalise_message(body)
            tx.write(
                "response",
                turn=turns,
                body=body,
                call_wall_s=round(call_wall, 3),
                prompt_tokens=p_tok,
                output_tokens=o_tok,
                finish_reason=finish_reason,
            )

            content = message.get("content") or ""
            tool_calls = message.get("tool_calls") or []
            tx.write(
                "assistant",
                turn=turns,
                content=content,
                n_tool_calls=len(tool_calls),
                reasoning=message.get("reasoning") or message.get("reasoning_content"),
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                    **({"tool_calls": tool_calls} if tool_calls else {}),
                }
            )

            if not tool_calls:
                stop_reason = "done"
                turns += 1
                break

            for idx, call in enumerate(tool_calls):
                fn = call.get("function") or {}
                name = fn.get("name") or ""
                raw = fn.get("arguments")
                call_id = call.get("id") or "call_%d_%d" % (turns, idx)
                parsed, violations = validate_call(name, raw)
                hard = [v for v in violations if v["kind"] != "extra_property"]
                tx.write(
                    "tool_call",
                    turn=turns,
                    index=idx,
                    id=call_id,
                    name=name,
                    arguments_raw=raw if isinstance(raw, str) else json.dumps(raw),
                    parsed_ok=parsed is not None,
                    violations=violations,
                    valid=(parsed is not None and not hard),
                    known_tool=name in toolschemas.TOOL_NAMES,
                )

                tool_t0 = time.time()
                injected = False
                if parsed is None:
                    # slbh tools.go:66-68 / :175 - a bad call is just a tool
                    # message, never a crashed turn.
                    kinds = {v["kind"] for v in violations}
                    if "unknown_tool" in kinds:
                        result, ok = 'tool error: unknown tool "%s"' % name, False
                    else:
                        detail = violations[0].get("detail", "")
                        result, ok = "tool error: tool arguments must be JSON: %s" % detail, False
                elif injector.should_fire(name, parsed):
                    injected = True
                    result, ok = "tool error: " + injector.message(), False
                else:
                    try:
                        out = executor.execute(name, parsed)
                        result, ok = out, True
                    except ToolError as exc:
                        result, ok = "tool error: " + str(exc), False
                    except Exception as exc:  # noqa: BLE001
                        result, ok = "tool error: %s: %s" % (type(exc).__name__, exc), False
                if len(result) > MAX_TOOL_RESULT_CHARS:
                    result = result[:MAX_TOOL_RESULT_CHARS] + "\n[truncated by leafloop]"
                tx.write(
                    "tool_result",
                    turn=turns,
                    index=idx,
                    id=call_id,
                    name=name,
                    ok=ok,
                    injected=injected,
                    duration_s=round(time.time() - tool_t0, 3),
                    output=result,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": name,
                        "content": result,
                    }
                )
            turns += 1
    except KeyboardInterrupt:
        stop_reason = "interrupted"
    except Exception:  # noqa: BLE001
        stop_reason = "loop_error"
        traceback_text = traceback.format_exc()
        tx.write("loop_error", traceback=traceback_text)
    finally:
        executor.shutdown()

    wall_s = time.time() - t0
    after_hash, after_files = sandbox_fingerprint(sandbox)
    changed = sorted(
        k for k in set(before_files) | set(after_files) if before_files.get(k) != after_files.get(k)
    )
    tx.write(
        "trial",
        stop_reason=stop_reason or "done",
        turns=turns,
        api_calls=api_calls,
        wall_s=round(wall_s, 3),
        prompt_tokens=prompt_tokens_total,
        output_tokens=output_tokens_total,
        peak_prompt=peak_prompt,
        last_prompt_tokens=last_prompt_tokens,
        injected_error_fired=injector.fired,
        sandbox_sha256_after=after_hash,
        changed_paths=changed,
        traceback=traceback_text,
        finished_at=time.time(),
    )
    tx.close()
    print(
        json.dumps(
            {
                "task": os.path.basename(task_dir),
                "stop_reason": stop_reason or "done",
                "turns": turns,
                "wall_s": round(wall_s, 3),
                "prompt_tokens": prompt_tokens_total,
                "output_tokens": output_tokens_total,
                "peak_prompt": peak_prompt,
                "transcript": os.path.abspath(args.transcript),
                "sandbox": sandbox,
                "changed_paths": changed,
            }
        )
    )
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task", required=True, help="task slot directory (holds prompt.md and seed/)")
    ap.add_argument("--sandbox", required=True, help="per-trial working directory; recreated")
    ap.add_argument("--transcript", required=True, help="per-trial JSONL transcript")
    ap.add_argument("--endpoint", default=None, help="e.g. http://host:11434 (not needed with --replay)")
    ap.add_argument("--api", choices=("openai", "native"), default="openai")
    ap.add_argument("--model", default="replay")
    ap.add_argument("--num-ctx", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--max-turns", type=int, default=40, help="slbh's own limit is 100 rounds")
    ap.add_argument("--wall-s", type=float, default=900.0)
    ap.add_argument("--http-timeout", type=float, default=600.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--replay", default=None, help="JSONL of canned assistant responses; no endpoint is called")
    ap.add_argument("--inject-error", default=None, help="JSON overriding the task's inject_error")
    ap.add_argument("--no-inject", action="store_true", help="disable the task's injected error")
    ap.add_argument("--agent-title", default="item1-leaf-trial")
    ap.add_argument("--runtime-id", default="rt-item1")
    ap.add_argument("--depth", type=int, default=2)
    args = ap.parse_args(argv)
    if args.replay is None and not args.endpoint:
        ap.error("--endpoint is required unless --replay is given")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
