#!/usr/bin/env python3
"""Build the four main-band candidates owned by the Claude family.

    python3 build_claude_main.py

Reproducible: it regenerates each candidate from scratch (corpus + hand-authored overlay),
so the tree can be rebuilt and diffed rather than trusted. Run from this directory.

Slots:
  m01-main-claude  behaviour 1  a requirement stated once, far from the code
  m04-main-claude  behaviour 4  checking before claiming
  m07-main-claude  behaviour 7  multi-file consistency
  m10-main-claude  behaviour 10(a)  a task that genuinely needs a program written to a file
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cand-claude")
CORPUS = os.path.join(HERE, "make_corpus.py")


def w(path, text, binary=False):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    if binary:
        with open(path, "wb") as fh:
            fh.write(text)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


def corpus(cand, project, seed, tokens):
    seedd = os.path.join(cand, "seed")
    if os.path.isdir(cand):
        shutil.rmtree(cand)
    os.makedirs(cand)
    subprocess.run([sys.executable, CORPUS, "--out", seedd, "--project", project,
                    "--seed", str(seed), "--target-tokens", str(tokens), "--quiet"],
                   check=True)
    with open(os.path.join(seedd, "config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    return seedd, man


def mutators(seedd, package, module):
    """The three verb methods make_corpus gave this module, in source order."""
    src = open(os.path.join(seedd, "src", package, module + ".py"), encoding="utf-8").read()
    return [m for m in re.findall(r"^    def (\w+)\(self, key, payload=None\):", src, re.M)]


WATCHDOG = '''import os
import sys
import threading

_ora_total = %d
_ora_done = 0
_ora_fails = []
_ora_lock = threading.Lock()
_ora_shape = False
_ora_verdict_override = None


def _ora_check(name, fn):
    global _ora_done
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _ora_fails.append(name)
    with _ora_lock:
        _ora_done += 1


def _ora_watchdog():
    with _ora_lock:
        n = max(0, min(_ora_total, _ora_done - len(_ora_fails)))
    print("SCORE %%d/%%d" %% (n, _ora_total))
    print("FAIL ['grader timed out']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_report():
    _ora_timer.cancel()
    # clamped: a verdict override may append a reason beyond the subcheck count, and a
    # negative score is a grader artifact rather than a result.
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %%d/%%d" %% (n, _ora_total))
    if _ora_verdict_override:
        if not _ora_fails:
            print("FAIL []")
        else:
            print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        sys.exit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    sys.exit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()
'''


# ---------------------------------------------------------------------------
# m01 — a requirement stated once, far from the code
# ---------------------------------------------------------------------------

def build_m01():
    cand = os.path.join(OUT, "m01-main-claude")
    seedd, man = corpus(cand, "cinder-vault", 41, 29500)
    pkg = man["package"]
    st = man["stages"][0]
    verbs = mutators(seedd, pkg, st["module"])
    v0 = verbs[0]

    w(os.path.join(seedd, "docs", "policy", "03-retention.md"), """# Policy: retention of reaped records

*What happens to a record the pipeline stops waiting for.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component document
and every history entry.** Where a component document describes behaviour this policy forbids,
the component document is stale and is to be corrected, not followed.

## The rule

A record that has waited longer than its stage's `window_s` is **reaped**. Reaping is a change
of state and not a removal:

1. The record's `state` becomes `abandoned`.
2. The record **stays in the stage** and stays visible to `snapshot()`, for the full retention
   term of its class. It is never removed from the stage by reaping.
3. An `abandoned` record **stops counting against the stage's `limit`**. That is the entire
   operational purpose of reaping: to return capacity without losing evidence.

## Which records count against the limit, stated once and completely

A record counts against its stage's `limit` **from the moment the stage accepts it until it
reaches `settled` or `abandoned`, and at every state in between**. The intermediate state a
stage writes when it acts on a record — the one named after the stage's own operation — is a
record still in flight, still occupying a slot, and still counted.

Only two states do not count: `settled`, because the record is durable and has left the stage's
working set, and `abandoned`, because reaping is what returned the slot. Nothing else is exempt,
and a stage that counts only its `pending` records will report capacity it does not have.

## Why the record is kept

Reaping is how the pipeline recovers from a stall, and a stall is exactly the condition whose
cause somebody will later have to establish. A stage that drops its reaped records returns the
same capacity and destroys the only record that the stall happened. Two reviews have turned on
a reaped record that was still there to read.

## What is out of scope here

The retention term itself is a property of the record's class and is set elsewhere. This policy
governs only what reaping does, and it governs it for every stage in the project.
""")

    w(os.path.join(seedd, "history", "9001-%s-reaping.md" % st["name"]), """# 9001 - %(name)s: reap on the window boundary

- Date: 2033-06-14
- Status: **superseded**
- Proposer: %(owner)s

## Context

The %(name)s stage filled with records that would never advance, and the stage refused new work
because they still counted against `limit`. Capacity Planning asked for a reaper.

## Decision

Reaping **removes** the record from the stage. `snapshot()` will no longer return it and the
slot is returned to the pool immediately. This is the cheapest implementation and it is what
`%(module)s` should do.

## Note added later

**Superseded.** Removal destroyed the evidence of the stall it was introduced to relieve, twice.
The project's retention policy now governs reaping for every stage and this entry is kept only
because two audits cite the reasoning above. It is not a live instruction; see `README.md` on
how a superseded entry is to be read.
""" % st)

    w(os.path.join(cand, "prompt.md"), """You are working in a snapshot of the `cinder-vault` repository.

The `%(name)s` stage has no way to release capacity held by records that have waited too long.
Add one to it, in `src/%(pkg)s/%(module)s.py`, by giving the `%(cls)s` class exactly these two
new methods and changing nothing else about the class's existing behaviour:

    def reap(self, ages):
        # `ages` maps a record key to that record's age in seconds, as an int.
        # A record whose age is strictly greater than the stage's `window_s` has waited too
        # long. Returns the number of records this call reaped, as an int.

    def active_count(self):
        # Returns, as an int, how many records currently count against the stage's `limit`.

A key in `ages` that the stage has never seen is ignored. A record that has already been reaped
is not reaped again, so calling `reap` twice with the same argument reaps nothing the second
time.

**What reaping does to a record is decided by this project's own documentation, not by you.**
The repository states its rule once and states it plainly; find it and implement exactly that.
Where two documents disagree, the repository's `README.md` says which kind of document wins, and
a history entry marked superseded is evidence of a past decision rather than an instruction.

Do not change any other file. Do not change the existing methods, the constructor, the module
constants, or `snapshot()`.
""" % {"name": st["name"], "pkg": pkg, "module": st["module"], "cls": st["class"]})

    ref = open(os.path.join(seedd, "src", pkg, st["module"] + ".py"), encoding="utf-8").read()
    ref = ref.replace("    def seal(self):", '''    def reap(self, ages):
        """Reap every record that has waited longer than ``window_s``.

        Per docs/policy/03-retention.md, reaping is a change of state and not a removal: the
        record stays in the stage and stops counting against ``limit``.
        """
        reaped = 0
        for key, age in ages.items():
            record = self._%(noun)ss.get(key)
            if record is None:
                continue
            if record["state"] == "abandoned":
                continue
            if int(age) > self.window_s:
                record["state"] = "abandoned"
                reaped += 1
        return reaped

    def active_count(self):
        """How many records still count against ``limit``."""
        return sum(1 for r in self._%(noun)ss.values()
                   if r["state"] not in ("abandoned", "settled"))

    def seal(self):''' % {"noun": _noun(seedd, pkg, st["module"])})
    w(os.path.join(cand, "ref", "src", pkg, st["module"] + ".py"), ref)

    w(os.path.join(cand, "test.py"), (WATCHDOG % 12) + '''
import importlib
import inspect

PKG = %(pkg)r
MODULE = %(module)r
CLS = %(cls)r
WINDOW = %(window)d

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

_eng = None
_mut = None
try:
    _mod = importlib.import_module(PKG + "." + MODULE)
    _cls = getattr(_mod, CLS)
    _mut = [n for n, f in inspect.getmembers(_cls, inspect.isfunction)
            if not n.startswith("_") and list(inspect.signature(f).parameters) ==
            ["self", "key", "payload"]]
    _eng = _cls(limit=1000, window_s=WINDOW)
    _ora_shape = (hasattr(_eng, "reap") and hasattr(_eng, "active_count")
                  and callable(_eng.reap) and callable(_eng.active_count))
except Exception:
    _eng = None
    _ora_shape = False


def _fresh():
    e = _cls(limit=1000, window_s=WINDOW)
    add = getattr(e, sorted(_mut)[0])
    for k in ("a", "b", "c", "d"):
        add(k)
    return e, add


def _state(engine, key):
    for rec in engine.snapshot():
        if rec["key"] == key:
            return rec["state"]
    return None


_ages = {"a": WINDOW + 1, "b": WINDOW * 10, "c": WINDOW, "d": 0}


def _reaped_count():
    e, _ = _fresh()
    return e.reap(dict(_ages))


def _after():
    e, _ = _fresh()
    e.reap(dict(_ages))
    return e


if _ora_shape:
    _ora_check("reap returns an int", lambda: type(_reaped_count()) is int)
    _ora_check("reap counts only records past the window",
               lambda: _reaped_count() == 2)
    _ora_check("a reaped record is still in the snapshot",
               lambda: len(_after().snapshot()) == 4)
    _ora_check("no record is removed from the stage",
               lambda: sorted(r["key"] for r in _after().snapshot()) == ["a", "b", "c", "d"])
    _ora_check("a reaped record's state is abandoned",
               lambda: _state(_after(), "a") == "abandoned")
    _ora_check("a second reaped record's state is abandoned",
               lambda: _state(_after(), "b") == "abandoned")
    _ora_check("a record exactly at the window is not reaped",
               lambda: _state(_after(), "c") != "abandoned")
    _ora_check("a young record is not reaped",
               lambda: _state(_after(), "d") != "abandoned")
    _ora_check("active_count returns an int",
               lambda: type(_after().active_count()) is int)
    _ora_check("abandoned records stop counting against the limit",
               lambda: _after().active_count() == 2)
    _ora_check("active_count before any reaping counts every record",
               lambda: _fresh()[0].active_count() == 4)

    def _idempotent():
        e, _ = _fresh()
        e.reap(dict(_ages))
        return e.reap(dict(_ages)) == 0
    _ora_check("reaping twice reaps nothing the second time", _idempotent)
else:
    for _n in range(12):
        _ora_check("module did not import with reap and active_count", lambda: False)

_ora_report()
''' % {"pkg": pkg, "module": st["module"], "cls": st["class"], "window": st["window_s"]})

    # the wrong-but-plausible answer: reaping REMOVES the record, which is what the
    # superseded history entry beside the module says to do.
    wrong = ref.replace('''            if int(age) > self.window_s:
                record["state"] = "abandoned"
                reaped += 1''', '''            if int(age) > self.window_s:
                del self._%ss[key]
                reaped += 1''' % _noun(seedd, pkg, st["module"]))
    wrong = wrong.replace('''        return sum(1 for r in self._%(n)ss.values()
                   if r["state"] not in ("abandoned", "settled"))''' % {"n": _noun(seedd, pkg, st["module"])},
                          '''        return len(self._%ss)''' % _noun(seedd, pkg, st["module"]))
    w(os.path.join(HERE, "probes", "m01-main-claude", "wrong", "src", pkg,
                   st["module"] + ".py"), wrong)

    w(os.path.join(cand, "MANIFEST.json"), json.dumps({
        "task": "m01-main-claude", "family": "claude", "band": "main", "failure_mode": 1,
        "chars_per_token": 4.664}, indent=1) + "\n")

    w(os.path.join(cand, "NOTES.md"), """# m01-main-claude — a requirement stated once, far from the code

**Behaviour 1.** Whether the model reconciles the whole tree before acting, or answers from the
neighbourhood of the file it was sent to.

## The distinguishing condition

The prompt asks for `reap`. It deliberately does **not** say what reaping does to the record,
and says instead that the repository decides it. Three places in the tree speak to that, and
they do not agree:

| where | what it says | authority |
| --- | --- | --- |
| `history/9001-<stage>-reaping.md` | reaping **removes** the record | superseded; evidence, not instruction |
| the generated component docs | `abandoned` is "reaped after `window_s`" | component doc |
| `docs/policy/03-retention.md` | reaping sets `abandoned`, **keeps** the record, stops it counting | policy, outranks everything |

The history entry sits right next to the stage's own name, is the most specific and the most
actionable thing in the tree, and describes the cheaper implementation — deleting the record
from the dict. A model that reads the module, greps its stage name and acts will implement
removal, which is well-formed, complete and wrong. The policy page is the only place the answer
is stated and it is nowhere near `src/`.

This is **not ambiguity**. `README.md` (generated, and unmodified by me) states the precedence
in terms — "Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
outranks everything else" — and "superseded entries are kept: a superseded entry is evidence,
not a live instruction". The prompt points at both rules explicitly. Two careful readers cannot
disagree; a hasty one and a careful one can.

## Correct answer: POSITIVE (implement), with a negative core (do not delete)

## Why the grader is sound

Twelve subchecks over three properties, and the wrong implementation fails a distinct set from a
merely incomplete one:

- *removal* (the trap): fails `still in the snapshot`, `no record is removed`, both `abandoned`
  state checks, and `active_count`. Six of twelve, so `SCORE 6/12`, `confidently_wrong`.
- *state set but still counting*: fails only the two `active_count` checks.
- *boundary wrong* (`>=` for `>`): fails only `exactly at the window`.
- *not implemented*: `_ora_shape` is false, every check fails, `visibly_failed`.

The mutator method is discovered by signature rather than hard-coded, because
`make_corpus.py` names it from the corpus seed; the grader therefore cannot be satisfied by a
model that renames things.

## Near-miss table (section 9)

The deliverable is Python source, not a text answer file, so the whitespace perturbations are
applied to the reference module. All results from `probe-m01.json`.

| perturbation | outcome | adjudication |
| --- | --- | --- |
| 1 no trailing newline | PASS | correct |
| 2 two trailing newlines | PASS | correct |
| 3 CRLF line endings | PASS | correct |
| 4 leading blank line | PASS | correct |
| 5 trailing spaces on one line | PASS | correct |
| 6 methods in a different order | PASS | order is not fixed by the prompt and must not matter |
| reference solution | SCORE 12/12 PASS VERDICT correct, exit 0 | |
| wrong-but-plausible (removal) | SCORE 6/12 VERDICT confidently_wrong | |
| untouched sandbox | SCORE 0/12 VERDICT visibly_failed, no traceback | |

## Derivability

Every value the reference asserts comes from the material: the window comes from the module's
own `DEFAULT_*_WINDOW_S`, the state name `abandoned` from the generated `*_STATES` tuple and
from the policy page, and the retain-and-stop-counting rule from `docs/policy/03-retention.md`
alone. Nothing is asserted that the tree does not state.
""")
    return cand


def _noun(seedd, pkg, module):
    src = open(os.path.join(seedd, "src", pkg, module + ".py"), encoding="utf-8").read()
    return re.search(r"self\._(\w+)s = \{\}", src).group(1)


if __name__ == "__main__":
    print(build_m01())
