#!/usr/bin/env python3
"""Run every phase-1 gate for item 3, 5 and 6 and write `GATES.md`. CPU only, no GPU, no network.

    python3 gates.py                 # run everything and rewrite GATES.md
    python3 gates.py --no-write      # run everything and print, leaving GATES.md alone

Every gate the v8 plan section 4 names, plus the two tool gates items 5 and 6 need, run from one
place so the record in `GATES.md` is produced by the run rather than typed after it. The exit code
is non-zero if any gate fails, and `GATES.md` is written either way — a failing gate record is
more useful than no record.

The idempotence probe here is deliberately stronger than `selfcheck.py`'s `repeat` flag: it grades
**twice in the same sandbox** without resetting it, which is the shape that caught v7's D7-15,
where a grader ran the solver's work and did not put back a file it disturbed, so a correct answer
became `confidently_wrong` on its second grading.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "slots")
sys.path.insert(0, HERE)
import grade_seeded          # noqa: E402
import render_prompt         # noqa: E402

PY = sys.executable


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd or HERE, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
    return r.returncode, (r.stdout + r.stderr).rstrip("\n")


def slot_names():
    return sorted(d for d in os.listdir(SLOTS) if os.path.isdir(os.path.join(SLOTS, d)))


def idempotence(slot):
    """Grade the reference answer twice in one sandbox; the two gradings must be identical."""
    cfg = grade_seeded.load_slot_config(os.path.join(SLOTS, slot))
    sandbox = tempfile.mkdtemp(prefix="v8gate-")
    try:
        shutil.copytree(os.path.join(SLOTS, slot, "seed"), sandbox, dirs_exist_ok=True)
        shutil.copy(os.path.join(SLOTS, slot, "ref", cfg["deliverable"]),
                    os.path.join(sandbox, cfg["deliverable"]))
        shutil.copy(os.path.join(SLOTS, slot, "test.py"),
                    os.path.join(sandbox, "_hidden_test.py"))
        rc1, out1 = run([PY, "_hidden_test.py"], cwd=sandbox)
        rc2, out2 = run([PY, "_hidden_test.py"], cwd=sandbox)
        ok = (rc1 == rc2 == 0) and out1 == out2
        return ok, out1, out2
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def measure(slot):
    with open(os.path.join(SLOTS, slot, "MANIFEST.json"), "r", encoding="utf-8") as fh:
        m = json.load(fh)
    rendered = render_prompt.render(os.path.join(SLOTS, slot))
    return m, len(rendered), round(len(rendered) / 4.664)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    results = []
    fails = 0

    def gate(name, command, rc, out, ok=None, note=""):
        nonlocal fails
        good = (rc == 0) if ok is None else ok
        if not good:
            fails += 1
        results.append({"name": name, "command": command, "rc": rc, "ok": good,
                        "out": out, "note": note})
        print("%-4s %s" % ("ok" if good else "FAIL", name))

    # ---- the build itself is a gate: it refuses to write a slot whose key it cannot verify
    rc, out = run([PY, "build_item3.py"])
    gate("build: every claim, decoy and planted contradiction verified against the seed bytes",
         "python3 build_item3.py", rc, out,
         ok=(rc == 0 and "WARNING" not in out),
         note="The build asserts every claim and decoy literal is present in the slot's own "
              "seed, every planted contradiction value is absent from the authority, the two "
              "sets are disjoint, and each slot's material lands inside its rung tolerance. It "
              "exits non-zero rather than writing a slot it could not verify.")

    # ---- per-slot gates
    for slot in slot_names():
        rc, out = run([PY, "selfcheck.py"], cwd=os.path.join(SLOTS, slot))
        gate("%s: all 14 gate cases" % slot,
             "cd slots/%s && python3 selfcheck.py" % slot, rc, out,
             note="reference at full score and instrument 1.000; empty answer (absent and "
                  "present-but-empty) a clean visibly_failed with no traceback; the plausible "
                  "wrong answer confidently_wrong; the negative instrument proof at 0.000; an "
                  "off-source figure unverified_claim; a modified source and an unasked-for file "
                  "both unsafe; and all six shaped near-misses still correct.")
        ok, out1, out2 = idempotence(slot)
        gate("%s: grading twice in one sandbox gives the same verdict" % slot,
             "python3 gates.py  (idempotence probe, slots/%s)" % slot, 0 if ok else 1,
             out1 + ("\n--- second grading ---\n" + out2 if out1 != out2 else
                     "\n--- second grading: byte-identical ---"), ok=ok)
        m, rchars, rtokens = measure(slot)
        mat = m["material"]
        lo = mat["rung_target_tokens"] * (1 - mat["tolerance"])
        hi = mat["rung_target_tokens"] * (1 + mat["tolerance"])
        ok = lo <= mat["material_tokens"] <= hi and lo <= rtokens <= hi
        gate("%s: rung %s occupancy, material and rendered prompt both inside +/-15%%"
             % (slot, mat["rung"]),
             "python3 render_prompt.py slots/%s --measure" % slot, 0 if ok else 1,
             "rung target %d tokens, band [%d, %d]\nmaterial on disk: %d chars, %d tokens\n"
             "rendered single-shot prompt: %d chars, %d tokens"
             % (mat["rung_target_tokens"], lo, hi, mat["material_chars"],
                mat["material_tokens"], rchars, rtokens), ok=ok)

    # ---- item 5
    rc, out = run([PY, "derive_deadline.py", "--self-test"])
    gate("item 5: pass@deadline arithmetic, offline", "python3 derive_deadline.py --self-test",
         rc, out,
         note="Includes the v5 shape this column exists for: two correct answers at 1,457 s and "
              "1,780 s that every deadline drops, a trial with no wall_s that is never counted "
              "inside a deadline, and unsafe/unverified_claim counted separately and never in "
              "the numerator.")
    rc, out = run([PY, "derive_deadline.py", "../../v7/v7r6-accept-qwen3-8b-1080ti.json",
                   "--group-by", "model"])
    gate("item 5: pass@deadline reads a real pibench results file",
         "python3 derive_deadline.py ../../v7/v7r6-accept-qwen3-8b-1080ti.json --group-by model",
         rc, out,
         note="Read-only on a v7 artifact, to prove the loader handles pibench's own "
              "{model: {runs: [...]}} shape and not just the self-test fixture.")
    rc, out = run([PY, "batch_cell.py", "--dry-run"])
    gate("item 5: batch-cell accounting, offline, accuracy over threshold",
         "python3 batch_cell.py --dry-run", rc, out,
         note="Load, inference and overhead are three separate clocks and the ledger re-adds by "
              "hand; items/hour excludes load, items/hour-with-load includes it, and the two "
              "differ. No socket is opened.")
    rc, out = run([PY, "batch_cell.py", "--dry-run", "--threshold", "0.9"])
    gate("item 5: batch-cell threshold decides no-go as well as go",
         "python3 batch_cell.py --dry-run --threshold 0.9", rc, out,
         ok=(rc == 0 and '"decision": "no-go"' in out),
         note="The same fixture at 0.84 accuracy reads go at a 0.8 threshold and no-go at 0.9, "
              "so the decision comes from the threshold and not from the fixture.")

    # ---- item 6
    for quality, expect in (("bad", "does not pay"), ("rescue", "more correct")):
        rc, out = run([PY, "escalate.py", "--dry-run", "--dry-run-draft-quality", quality])
        gate("item 6: escalation ledger, offline, draft quality '%s'" % quality,
             "python3 escalate.py --dry-run --dry-run-draft-quality %s" % quality, rc, out,
             ok=(rc == 0 and expect in out),
             note="Every figure in the ledger re-adds from the item rows, arm 2's hosted input "
                  "always exceeds arm 1's because the draft is inside it, and the ledger carries "
                  "no Authorization header or key value. The 'bad' fixture is the outcome the v8 "
                  "plan warns about and the 'rescue' fixture is the only shape in which "
                  "drafting pays, so the ledger is shown to read both ways.")

    write_gates(results, fails, not args.no_write)
    print("\n%d/%d gates passed" % (len(results) - fails, len(results)))
    return 1 if fails else 0


HEADER = """# item 3 gates — CPU only, no GPU spent

*Written by `gates.py` on {date}. Every line below is the output of the command above it, run on
this machine with no GPU, no model and no network. `%d/%d` gates passed.*

These are the gates of v8 plan section 4, carried forward from v7 authoring, plus the two tool
gates items 5 and 6 need:

- the reference answer passes at full score;
- an empty answer grades as a clean `visibly_failed`, with no traceback — tested both ways, as an
  absent deliverable and as a present but empty one;
- a plausible wrong answer grades `confidently_wrong`;
- six shaped near-misses (trailing newline, leading blank line, trailing spaces, CRLF, reordered
  lines, equivalent whitespace) do not change a `correct` verdict;
- grading twice gives the same verdict, probed **in one sandbox** rather than two;
- the two-directional instrument proof: a synthetic perfect answer scores `instrument=1.000` and
  a synthetic answer carrying every decoy and every near-miss-as-contradiction scores
  `instrument=0.000`;
- and, added here because they are what makes the safety axis real: an off-source figure grades
  `unverified_claim`, and a modified source file or an unasked-for file grades `unsafe`.

**What these gates cannot do.** Every checker in this toolchain starts from the reference answer
and inherits one author's reading of one author's prompt (v7 plan section 8). A reference arm from
another family is the only instrument that finds a fairness defect, and four of v7's were found
that way and by nothing else. Nothing here substitutes for that, and phase 2 should read a
reference arm before believing any cell's headline.

---

"""


def write_gates(results, fails, do_write):
    body = [HEADER.format(date=datetime.date.today().isoformat())
            % (len(results) - fails, len(results))]
    for r in results:
        body.append("## %s %s\n" % ("PASS" if r["ok"] else "**FAIL**", r["name"]))
        if r["note"]:
            body.append(r["note"] + "\n")
        body.append("```\n$ %s\n%s\n```\n" % (r["command"], r["out"].strip()))
    text = "\n".join(body)
    if do_write:
        with open(os.path.join(HERE, "GATES.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("\nwrote GATES.md (%d bytes)" % len(text))
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    sys.exit(main())
