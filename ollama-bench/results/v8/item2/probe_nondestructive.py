#!/usr/bin/env python3
"""Prove that nothing in item 2 can damage a tracked file.

    python3 probe_nondestructive.py

Item 1's gate run cleared 89 tracked report files when it crashed midway, and item 3's
wiped a slot it could not then rebuild. That makes "my scripts are non-destructive" a claim
to be verified, not asserted, so this measures it five ways:

  N1  `write_slot` failing partway through leaves the slot on disk byte-for-byte as it was,
      and leaves no staging directory behind.
  N2  `_swap_dir` failing to move the replacement into place puts the committed slot back.
  N3  `write_text_atomic` failing leaves the original file's bytes intact -- the case plain
      `open(path, "w")` gets wrong, because it truncates before it writes.
  N4  `refprobe.py` changes not one byte anywhere under `item2/`.
  N5  every other subprocess `gates.py` launches -- `selfcheck.py`, `score_abstention.py`,
      `probe_extra.py` -- changes not one byte anywhere under `item2/`.

N4 and N5 together account for every subprocess `gates.py` runs, so the only writes left in
`gates.py` itself are `GATES.md` and `GATES.json`, both of which go through the
`write_text_atomic` proven by N3.

Exits 0 only when all five hold. Touches no GPU and no endpoint.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "slots")
sys.path.insert(0, HERE)
import common                                                   # noqa: E402

failures = []


def tree_digest(root, skip=()):
    """path -> sha256 for every file under `root`, excluding `skip` and caches."""
    out = {}
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in sorted(names):
            p = os.path.join(base, n)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            if rel in skip or n.endswith(".pyc"):
                continue
            with open(p, "rb") as fh:
                out[rel] = common.hashlib.sha256(fh.read()).hexdigest()
    return out


def strays():
    return sorted(d for d in os.listdir(SLOTS) if d.startswith("."))


def check(label, ok, detail=""):
    print("  %s %s%s" % ("ok  " if ok else "FAIL", label,
                         "" if ok else "  <- " + detail))
    if not ok:
        failures.append("%s: %s" % (label, detail))


def dummy_args():
    return dict(prompt="replacement prompt\n",
                config={"items": [], "example": {"shape": "aggregate", "stated": {}}},
                items=[], ref_answer={}, decoy_answer={}, plausible_answer={},
                notes="replacement notes\n", manifest={"generator": "probe"}, here=HERE)


# ---------------------------------------------------------------- N1 and N2
victim = sorted(d for d in os.listdir(SLOTS) if os.path.isdir(os.path.join(SLOTS, d)))[0]
target = os.path.join(SLOTS, victim)
before = tree_digest(target)

for label, nth in (("N1 write_slot fails on its first write", 1),
                   ("N1 write_slot fails after the ref files are written", 5)):
    real_w, calls = common._w, [0]

    def boom(path, text, _real=real_w, _calls=calls, _nth=nth):
        _calls[0] += 1
        if _calls[0] >= _nth:
            raise RuntimeError("injected failure on write %d" % _calls[0])
        return _real(path, text)

    common._w = boom
    try:
        common.write_slot(target, **dummy_args())
        raised = False
    except RuntimeError:
        raised = True
    finally:
        common._w = real_w
    after = tree_digest(target)
    check(label, raised and after == before and not strays(),
          "raised=%s changed=%s strays=%s"
          % (raised, sorted(set(before) ^ set(after))
             or [k for k in before if before[k] != after.get(k)], strays()))

real_rename = os.rename


def rename_once_then_fail(src, dst, _real=real_rename, _state=[0]):
    _state[0] += 1
    if _state[0] == 2:                     # the move of the replacement into place
        raise OSError("injected rename failure")
    return _real(src, dst)


os.rename = rename_once_then_fail
try:
    common.write_slot(target, **dummy_args())
    raised = False
except OSError:
    raised = True
finally:
    os.rename = real_rename
after = tree_digest(target)
check("N2 _swap_dir fails and the committed slot is put back",
      raised and after == before and not strays(),
      "raised=%s equal=%s strays=%s" % (raised, after == before, strays()))

# ---------------------------------------------------------------- N3
box = tempfile.mkdtemp(prefix="v8i2nd_")
try:
    probe_file = os.path.join(box, "tracked.md")
    original = "the committed bytes\n"
    with open(probe_file, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(original)
    real_replace = os.replace
    os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("injected"))
    try:
        common.write_text_atomic(probe_file, "replacement\n")
        raised = False
    except OSError:
        raised = True
    finally:
        os.replace = real_replace
    with open(probe_file, encoding="utf-8") as fh:
        kept = fh.read()
    left = [n for n in os.listdir(box) if n != "tracked.md"]
    check("N3 write_text_atomic fails and the original bytes survive",
          raised and kept == original and not left,
          "raised=%s kept=%r leftovers=%s" % (raised, kept, left))
    # and it does replace the file when nothing goes wrong
    common.write_text_atomic(probe_file, "replacement\n")
    with open(probe_file, encoding="utf-8") as fh:
        check("N3 write_text_atomic replaces the file when it succeeds",
              fh.read() == "replacement\n")
finally:
    shutil.rmtree(box, ignore_errors=True)

# ---------------------------------------------------------------- N4 and N5
SKIP = ("GATES.md", "GATES.json")
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
           PYTHONDONTWRITEBYTECODE="1")
runs = [
    ("N4 refprobe.py", [sys.executable, "refprobe.py"], HERE),
    ("N5 probe_extra.py", [sys.executable, "probe_extra.py"], HERE),
    ("N5 score_abstention.py",
     [sys.executable, "score_abstention.py", "--slot", os.path.join("slots", victim),
      "--answer", "ref/answer.json", "ref/decoy_answer.json", "--quiet"], HERE),
    ("N5 selfcheck.py", [sys.executable, "selfcheck.py"], os.path.join(SLOTS, victim)),
]
for label, cmd, cwd in runs:
    snap = tree_digest(HERE, skip=SKIP)
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    again = tree_digest(HERE, skip=SKIP)
    changed = sorted(k for k in set(snap) | set(again) if snap.get(k) != again.get(k))
    check("%s leaves every file under item2/ untouched" % label,
          p.returncode == 0 and not changed and not strays(),
          "exit=%d changed=%s strays=%s" % (p.returncode, changed, strays()))

# ---------------------------------------------------------------- restore and report
print("\nthe slot used for the injection tests, %s, is byte-identical to its committed "
      "state: %s" % (victim, tree_digest(target) == before))
if failures:
    print("\nFAILURES (%d):" % len(failures))
    for f in failures:
        print("  - %s" % f)
    sys.exit(1)
print("ALL CLEAR -- nothing in item 2 can damage a tracked file")
sys.exit(0)
