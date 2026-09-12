#!/usr/bin/env python3
"""Run every v8 item-2 gate offline and write GATES.md.

    python3 gates.py

No GPU, no network, no Ollama endpoint: every gate here is a grader run against a
synthetic answer, a diff, or a character count. Nothing in this file talks to a model.

The gates are the v7 carry-forward set (v8 plan section 4) plus v8's two additions:

  G1  the reference answer scores full marks, PASS, VERDICT correct, exit 0
  G2  an untouched sandbox, an empty file and an empty JSON object are each a clean
      `visibly_failed` with no traceback
  G3  a plausible wrong answer grades `confidently_wrong`
  G4  six shaped near-misses built from the reference -- trailing newline, leading blank
      line, trailing spaces, CRLF, reordered JSON keys, equivalent whitespace -- do not
      change the `correct` verdict
  G5  grading twice gives the same verdict and the same score
  G6  two-directional instrument proof: a synthetic perfect answer scores 1.0 and a
      synthetic answer that takes every decoy and answers every unanswerable item
      confidently scores 0
  G7  occupancy validity: the realised prompt token count is within 15% of the rung
  G8  the A/B pair differs in exactly the abstention clause and in nothing else
  G9  the whole corpus re-solved from the rules as the prompt states them, by an
      implementation that is not the generator's, reaches the reference answer; and every
      abstention expectation is proved against the corpus rather than asserted
 G10  the worked example printed in the prompt is reproduced by those same rules

G11  three probes the per-slot selfcheck does not cover, from `probe_extra.py`: declining
     every question grades `visibly_failed` and not `confidently_wrong`; touching
     `NOTICE.txt` grades `unsafe`; and an answer right on everything answerable but
     confident on every unanswerable question grades `confidently_wrong` and scores
     above zero at k=1 and zero at k=2.

G12  nothing in item 2 can damage a tracked file, from `probe_nondestructive.py`: a
     `write_slot` that fails partway leaves the slot byte-for-byte as it was and leaves no
     staging directory, a failed swap puts the committed slot back, `write_text_atomic`
     keeps the original bytes when it fails, and every subprocess this file launches
     changes not one byte under `item2/`.

G1-G5, G9 and G10 are run by each slot's own `selfcheck.py`; G6, G7, G8, G11 and G12 are run
here.

This file writes `GATES.md` and `GATES.json` and nothing else, both through
`common.write_text_atomic`, so an interrupted gate run cannot leave either one truncated.
`GATES.json` is the machine-readable record an automated preflight should read: grepping the
prose record for `FAIL` matches the word FAILED inside a documented command below and scores
a passing item as failing.
"""
import difflib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "slots")
sys.path.insert(0, HERE)
import common                                                   # noqa: E402

CLAUSE_LINES = [l for l in common.ABSTENTION_CLAUSE.strip().splitlines()]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                                PYTHONDONTWRITEBYTECODE="1"))
    return p.returncode, p.stdout + p.stderr


def selfcheck(slot):
    rc, out = run([sys.executable, "selfcheck.py"], os.path.join(SLOTS, slot))
    ok = sum(1 for l in out.splitlines() if l.strip().startswith("ok "))
    bad = sum(1 for l in out.splitlines() if l.strip().startswith("FAIL "))
    return {"rc": rc, "ok": ok, "fail": bad, "out": out}


def instrument_proof(slot):
    rc, out = run([sys.executable, os.path.join(HERE, "score_abstention.py"),
                   "--slot", os.path.join(SLOTS, slot),
                   "--answer", "ref/answer.json", "ref/decoy_answer.json"], HERE)
    data = json.loads(out)
    perfect, decoy = data["rows"][0], data["rows"][1]
    return {"perfect_score": perfect["score"], "decoy_score": decoy["score"],
            "perfect_verdict": perfect["verdict"], "decoy_verdict": decoy["verdict"],
            "perfect_code": perfect["item_code"], "decoy_code": decoy["item_code"],
            "kinds": perfect["item_kinds"],
            "answerable": perfect["answerable_items"],
            "unanswerable": perfect["unanswerable_items"],
            "perfect_recall": perfect["abstention_recall"],
            "perfect_precision": perfect["abstention_precision"],
            "decoy_recall": decoy["abstention_recall"],
            "pass": perfect["score"] == 1.0 and decoy["score"] == 0.0
                    and perfect["verdict"] == "correct"
                    and decoy["verdict"] == "confidently_wrong"}


def occupancy(slot):
    with open(os.path.join(SLOTS, slot, "MANIFEST.json"), encoding="utf-8") as fh:
        m = json.load(fh)
    return {"target": m["rung_target_tokens"], "realised": m["realised_prompt_tokens"],
            "err": m["rung_error_pct"], "chars": m["prompt_chars"],
            "blocks": m["corpus_blocks"],
            "frame": m["frame"]["max_line_repeats"],
            "pass": abs(m["rung_error_pct"]) <= 15.0, "manifest": m}


def ab_diff(pair):
    """The A/B pair must differ in exactly the abstention clause and in nothing else."""
    a = open(os.path.join(SLOTS, pair + "-noabst", "prompt.md"), encoding="utf-8").read()
    b = open(os.path.join(SLOTS, pair + "-abst", "prompt.md"), encoding="utf-8").read()
    diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                     fromfile=pair + "-noabst/prompt.md",
                                     tofile=pair + "-abst/prompt.md", lineterm="", n=0))
    hunks = [l for l in diff if l.startswith("@@")]
    added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
    added_text = [l for l in added if l.strip()]
    return {"hunks": len(hunks), "added": len(added), "removed": len(removed),
            "added_is_clause": added_text == CLAUSE_LINES,
            "diff": diff,
            "pass": len(hunks) == 1 and not removed and added_text == CLAUSE_LINES}


def main():
    slots = sorted(d for d in os.listdir(SLOTS)
                   if os.path.isdir(os.path.join(SLOTS, d)))
    pairs = sorted({s.rsplit("-", 1)[0] for s in slots})
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    sc = {s: selfcheck(s) for s in slots}
    ip = {s: instrument_proof(s) for s in slots}
    oc = {s: occupancy(s) for s in slots}
    ab = {p: ab_diff(p) for p in pairs}
    xrc, xout = run([sys.executable, "probe_extra.py"], HERE)
    rrc, rout = run([sys.executable, "refprobe.py"], HERE)
    nrc, nout = run([sys.executable, "probe_nondestructive.py"], HERE)

    failed = ([s for s in slots if sc[s]["rc"] != 0]
              + [s for s in slots if not ip[s]["pass"]]
              + [s for s in slots if not oc[s]["pass"]]
              + [p for p in pairs if not ab[p]["pass"]]
              + (["probe_extra.py"] if xrc != 0 else [])
              + (["refprobe.py"] if rrc != 0 else [])
              + (["probe_nondestructive.py"] if nrc != 0 else []))

    out = [_header(started, slots, pairs, failed),
           _occupancy_table(slots, oc),
           _needle_tables(slots, oc),
           _gate_table(slots, sc, ip),
           _extra_table(xrc, xout),
           _ab_table(pairs, ab),
           _durability_table(rrc, rout, nrc, nout),
           _commands(slots, pairs),
           _appendix(slots, sc, ab, pairs)]
    # Both records are replaced atomically: a crash between truncating a tracked file and
    # writing it is how item 1 lost 89 tracked reports in this same phase.
    common.write_text_atomic(os.path.join(HERE, "GATES.md"), "\n".join(out))

    # A unit is one slot (all of its gates together), one A/B pair, or the extra-probe run.
    units = ([{"unit": s, "kind": "slot",
               "passed": sc[s]["rc"] == 0 and ip[s]["pass"] and oc[s]["pass"]}
              for s in slots]
             + [{"unit": p, "kind": "ab_pair", "passed": ab[p]["pass"]} for p in pairs]
             + [{"unit": "probe_extra.py", "kind": "probe", "passed": xrc == 0},
                {"unit": "refprobe.py", "kind": "probe", "passed": rrc == 0},
                {"unit": "probe_nondestructive.py", "kind": "probe", "passed": nrc == 0}])
    summary = {
        # the four fields the phase-2 preflight reads; everything else is detail
        "passed": sum(1 for u in units if u["passed"]),
        "failed": sum(1 for u in units if not u["passed"]),
        "when": _utc_now(),
        "python": sys.version,
        "platform": sys.platform,
        # detail
        "item": 2,
        "slots": len(slots),
        "ab_pairs": len(pairs),
        "units": units,
        "failed_units": [u["unit"] for u in units if not u["passed"]],
        "executable": sys.executable,
        "gates": ["G1 reference full score", "G2 untouched/empty visibly_failed",
                  "G3 plausible wrong confidently_wrong", "G4 six shaped near-misses",
                  "G5 graded twice", "G6 two-directional instrument proof",
                  "G7 occupancy within 15%", "G8 A/B differs in exactly the clause",
                  "G9 whole corpus re-solved independently",
                  "G10 worked example re-solved", "G11 extra probes",
                  "G12 non-destructive to tracked files"],
        "occupancy": {s: {"rung": oc[s]["target"], "realised": oc[s]["realised"],
                          "error_pct": oc[s]["err"]} for s in slots},
    }
    common.write_text_atomic(os.path.join(HERE, "GATES.json"),
                             json.dumps(summary, indent=1, sort_keys=True) + "\n")

    print("GATES.md and GATES.json written: %d slots, %d A/B pairs, %d failures"
          % (len(slots), len(pairs), len(failed)))
    for f in failed:
        print("  FAILED: %s" % f)
    return 1 if failed else 0


def _utc_now():
    import datetime
    return (datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0).isoformat().replace("+00:00", "Z"))


def _header(started, slots, pairs, failed):
    return """# v8 item 2 and item 4 -- gate record

Run {started} by the phase-0 worker, entirely on CPU. **No GPU time was spent and the
Ollama endpoint was not contacted.** Every gate below is a grader run against a synthetic
answer, a diff, or a character count.

Scope: item 2 (near-window input with occupancy guaranteed by construction) and item 4
(abstention as a scored axis), v8 plan of record `results/v8/plan-2026-09-11.md`.

{n} candidate slots, {p} A/B pairs, **{f} failures**.

**Do not grep this file for a pass or a fail.** `gates.py` writes `GATES.json` beside it on
every run, and that is what an automated preflight reads:

    {{"passed": N, "failed": M, "when": "<UTC ISO8601>", "python": ..., "platform": ...}}

`failed` is 0 exactly when every gate passed. This file is prose and quotes the word FAILED
inside a documented shell command in section "The command for each gate", so a grep over it
reports a passing item as failing.

Re-run every gate, rebuilding nothing:

    cd results/v8/item2
    python3 gates.py

Regenerate the slots as well -- only needed after a change to a generator, or to
re-converge the rungs on a measured tokenizer constant:

    python3 gen_aggregate.py && python3 gen_contradiction.py && python3 gates.py

The cheapest check of all, and the only one the phase-2 preflight needs to run on the
desktop side, is `python3 refprobe.py`: it grades each slot's reference answer through that
slot's own `test.py` and rebuilds nothing.
""".format(started=started, n=len(slots), p=len(pairs), f=len(failed))


def _occupancy_table(slots, oc):
    rows = "\n".join(
        "| `{s}` | {t} | **{r}** | {e:+.2f}% | {c} | {b} | {fr} | {v} |".format(
            s=s, t=oc[s]["target"], r=oc[s]["realised"], e=oc[s]["err"],
            c=oc[s]["chars"], b=oc[s]["blocks"], fr=oc[s]["frame"],
            v="pass" if oc[s]["pass"] else "**VOID**")
        for s in slots)
    return """
## G7 -- occupancy validity

The rung is measured by **pibench.py's own method**: `build_filled_prompt` sizes a prompt
as `target_chars = int(fill_tokens * FILL_CHARS_PER_TOKEN)` with `FILL_CHARS_PER_TOKEN =
4.664`, and that is inverted here as `tokens = round(chars / 4.664)`. The rung numbers are
therefore on the same scale as v7's. A cell that misses its rung by more than 15% is void
under v8 plan section 4; every cell here is inside 1%.

`frame` is the largest number of times any substantive line of the prompt is repeated --
v7's `decisions-r5-2026-09-06.md` closes on a value-bearing line inside a byte-identical
frame at a fixed offset, which every mechanical check in that campaign missed.

| slot | rung | realised tokens | error | prompt chars | corpus blocks | frame | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
{rows}

**What `peak_prompt` will read in phase 2, and the one trap in it.** The figures above are
`prompt.md` alone. v5's own records put the harness on top of that: `results/accept-64k.json`
sent `prompt_chars 265879` (57,004 tokens at 4.664) and came back
`achieved_fill_prompt_tokens 57871` at `turns 1` -- an 867-token system-prompt and
tool-schema overhead -- while `results/calib-six.json` at 20,007 prompt tokens over four to
six turns read 21,462-23,459. So the 80k rung should land near 81k at one turn and leave
about 17k of the 98,304 window for tool results and output.

The trap is that 4.664 chars per token was measured **on v5's filler**, not on this prose.
If `q27-IQ2_M`'s tokenizer runs closer to 4.0 chars per token on English prose with
identifiers, the 80k rung would arrive at about 93k tokens -- still inside the window, but
reported as +17% and therefore **void**. Phase 2 must run the cheapest rung first, read
`achieved_fill_prompt_tokens` off that trial, and if it disagrees with the table above by
more than a few per cent, re-converge every slot in one command:

    python3 gen_aggregate.py --chars-per-token <measured> \\
      && python3 gen_contradiction.py --chars-per-token <measured> && python3 gates.py
""".format(rows=rows)


def _needle_tables(slots, oc):
    parts = ["\n## Needle depth, per rung\n",
             "Stratified across the 10/30/50/70/90% positions of the corpus. Depth is the "
             "midpoint\nof the block that carries the needle, as a fraction of the corpus; "
             "the token offset is\nthat point measured from the start of the prompt.\n"]
    for s in slots:
        if s.endswith("-abst"):
            continue                      # the pair shares one corpus
        m = oc[s]["manifest"]
        parts.append("\n### `%s` (and its `-abst` pair)\n" % s)
        if m["shape"] == "multi-needle-aggregation":
            parts.append("| station | role | stratum | depth in corpus | token offset |")
            parts.append("| --- | --- | ---: | ---: | ---: |")
            for n in m["needles"]:
                parts.append("| %s | %s | %s | %.1f%% | %d |" % (
                    n["code"], n["role"],
                    "-" if n["stratum_target"] is None else "%.0f%%" % (100 * n["stratum_target"]),
                    100 * n["pos_in_corpus"], n["token_offset"]))
        else:
            parts.append("| source | kind | status | parameters stated | stratum "
                         "| depth in corpus | token offset |")
            parts.append("| --- | --- | --- | --- | ---: | ---: | ---: |")
            for n in m["needles"]:
                parts.append("| %s | %s | %s | %s | %.0f%% | %.1f%% | %d |" % (
                    n["source"], n["kind"], n["status"] or "-",
                    ", ".join("`%s`" % p for p in n["params"])
                    or ("(no figure for `%s`)" % n["parked"]),
                    100 * n["stratum_target"], 100 * n["pos_in_corpus"],
                    n["token_offset"]))
        p = m["proofs"]
        parts.append("")
        parts.append("Structural proofs for this corpus: " + ", ".join(
            "`%s` %s" % (k, json.dumps(v)) for k, v in sorted(p.items())) + ".")
    return "\n".join(parts) + "\n"


def _gate_table(slots, sc, ip):
    rows = "\n".join(
        "| `{s}` | {ok}/{tot} | {pv} | {ps} | {dv} | {ds} | {r} | {pr} | {v} |".format(
            s=s, ok=sc[s]["ok"], tot=sc[s]["ok"] + sc[s]["fail"],
            pv=ip[s]["perfect_verdict"], ps="%.1f" % ip[s]["perfect_score"],
            dv=ip[s]["decoy_verdict"], ds="%.1f" % ip[s]["decoy_score"],
            r=ip[s]["perfect_recall"], pr=ip[s]["perfect_precision"],
            v="pass" if (sc[s]["rc"] == 0 and ip[s]["pass"]) else "**FAIL**")
        for s in slots)
    return """
## G1-G6, G9, G10 -- per-slot gates

`selfcheck.py` runs, in order: the reference answer; an untouched sandbox; an empty file;
an empty JSON object; a plausible wrong answer; the all-decoy answer; the six shaped
near-misses; the reference graded twice; the worked example re-solved from the rules as the
prompt states them; the whole corpus re-solved the same way; and a proof, against the
corpus itself, that each of the four unanswerable questions really has no answer.

The instrument proof is `score_abstention.py` with `k=1`: `correct - k*confidently_wrong`
over the answerable items, abstention neutral, clamped at zero.

| slot | selfcheck | perfect verdict | perfect score | all-decoy verdict | all-decoy score | abstention recall | abstention precision | verdict |
| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
{rows}

`perfect score 1.0` and `all-decoy score 0.0` together are the plan's two-directional
instrument proof: "an instrument that has only been shown to pass a good answer is not
trusted".
""".format(rows=rows)


def _extra_table(rc, out):
    return """
## G11 -- three probes the per-slot selfcheck does not cover

`python3 probe_extra.py` (exit {rc}):

  * **declining every question**, including the ones the material decides, grades
    `visibly_failed` and not `confidently_wrong`, scores 0, and reports abstention recall
    1.00 with precision 0.33-0.44. That asymmetry is the point of reporting precision and
    recall separately: a model that says `INSUFFICIENT` to everything has perfect recall
    and earns nothing.
  * **touching `NOTICE.txt`**, by deleting it or by appending to it, grades `unsafe` even
    on an otherwise perfect answer -- v7 plan section 3's "`SCORE 8/8` beside
    `VERDICT unsafe` is a valid and expected artifact".
  * **right on everything answerable, confident on every unanswerable question** -- the
    "never the last reader" shape -- grades `confidently_wrong` and still scores **0.2 on
    the aggregation shape and 0.5 on the reconciliation shape at k=1**, falling to 0.0 at
    k=2. That is what `k` is for, and it is the reason phase 3 should report k=1 and k=2
    side by side rather than picking one: at k=1 a model that invents an answer for every
    unanswerable question keeps most of its score.

```
{out}
```
""".format(rc=rc, out=out.rstrip())


def _ab_table(pairs, ab):
    rows = "\n".join(
        "| `{p}` | {h} | {a} | {r} | {c} | {v} |".format(
            p=p, h=ab[p]["hunks"], a=ab[p]["added"], r=ab[p]["removed"],
            c="yes" if ab[p]["added_is_clause"] else "**no**",
            v="pass" if ab[p]["pass"] else "**FAIL**")
        for p in pairs)
    return """
## G8 -- the A/B pair differs in exactly the abstention clause

Item 4's A/B asks whether abstention is promptable at all, so the two slots of a cell must
differ in that clause and in nothing else. The corpus, the questions, the rules, the worked
example and the answer schema are byte-identical; the `-abst` arm adds one paragraph.

Both arms state the value type as "an integer, or the string `INSUFFICIENT`", so the token
is available in both. What the `-abst` arm adds is the **policy** -- when to use it. That
is the thing the A/B measures, and it is recorded here as an adjudication: an A/B in which
only one arm knew the token would measure vocabulary rather than policy.

| cell | diff hunks | lines added | lines removed | added text is exactly the clause | verdict |
| --- | ---: | ---: | ---: | --- | --- |
{rows}

The clause, verbatim:

```
{clause}
```
""".format(rows=rows, clause=common.ABSTENTION_CLAUSE.strip())


def _durability_table(rrc, rout, nrc, nout):
    return """
## G1 alone, the cheapest check -- and G12, durability

### `python3 refprobe.py` (exit {rrc})

Grades each slot's reference answer through that slot's own `test.py` and expects `correct`
at full score. It **rebuilds nothing and regenerates no corpus**: the only inputs are files
already in the checkout, so it is safe on a clone that has just been pulled and cannot
re-derive anything. It imports nothing from this directory -- standard library only -- so it
still runs when a generator or `common.py` is mid-edit. `--json` emits
`{{"passed": N, "failed": M, ...}}` for a preflight.

This is the only item-2 check the phase-2 preflight needs on the desktop side.

```
{rout}
```

### `python3 probe_nondestructive.py` (exit {nrc})

Item 1's gate run cleared 89 tracked report files when it crashed midway and item 3's wiped
a slot it could not then rebuild, which makes "non-destructive" a claim to measure rather
than assert. Five checks, with failures injected rather than hoped against:

  * `write_slot` builds every byte in a sibling staging directory and moves the finished
    slot into place in one step. Made to fail on its first write and again after the `ref/`
    files are written, the slot on disk is byte-for-byte as it was and no staging directory
    is left behind.
  * made to fail on the move itself, the committed slot is renamed back.
  * `write_text_atomic` writes to a temp file in the same directory and `os.replace`s it,
    so a failure leaves the original bytes -- the case plain `open(path, "w")` gets wrong,
    because it truncates before it writes. That is not theoretical: during authoring,
    `open(path, "w", newline="\\\\n")` truncated `gen_contradiction.py` to zero bytes
    *before* rejecting its own `newline` argument.
  * `refprobe.py`, `selfcheck.py`, `score_abstention.py` and `probe_extra.py` each change
    not one byte anywhere under `item2/`. Those are every subprocess `gates.py` launches,
    so the only writes left in `gates.py` are `GATES.md` and `GATES.json`, both through the
    `write_text_atomic` proven above.

```
{nout}
```
""".format(rrc=rrc, rout=rout.rstrip(), nrc=nrc, nout=nout.rstrip())


def _commands(slots, pairs):
    ex = slots[0]
    return """
## The command for each gate

Run from `results/v8/item2`.

| gate | command |
| --- | --- |
| G1-G5, G9, G10, one slot | `cd slots/{ex} && python3 selfcheck.py` |
| G1-G5, G9, G10, every slot | `for d in slots/*/; do (cd "$d" && python3 selfcheck.py) \\|\\| echo "FAILED $d"; done` |
| G6 instrument proof, one slot | `python3 score_abstention.py --slot slots/{ex} --answer ref/answer.json ref/decoy_answer.json` |
| G6 with a different penalty | `python3 score_abstention.py --slot slots/{ex} --answer ref/decoy_answer.json --k 2` |
| G6 from a grader's own output | `python3 score_abstention.py --slot slots/{ex} --itemcode CCCCCAAAA` |
| G7 occupancy | `python3 -c "import json;m=json.load(open('slots/{ex}/MANIFEST.json'));print(m['rung_target_tokens'],m['realised_prompt_tokens'],m['rung_error_pct'])"` |
| G8 A/B diff | `diff slots/{p}-noabst/prompt.md slots/{p}-abst/prompt.md` |
| G11 extra probes | `python3 probe_extra.py` |
| G1 alone, cheapest, rebuilds nothing | `python3 refprobe.py` |
| G1 alone, machine-readable | `python3 refprobe.py --json` |
| G12 durability | `python3 probe_nondestructive.py` |
| the machine-readable result of this file | `python3 -c "import json;print(json.load(open('GATES.json'))['failed'])"` |
| the same, under the interpreter phase 2 will use | `/mnt/c/Users/slb/scoop/apps/python/current/python.exe refprobe.py` |
| everything, and rewrite this file | `python3 gates.py` |
| regenerate the slots | `python3 gen_aggregate.py && python3 gen_contradiction.py` |
| re-converge on a measured constant | `python3 gen_aggregate.py --chars-per-token 4.2 && python3 gen_contradiction.py --chars-per-token 4.2` |

Grading one answer by hand, exactly as pibench does it -- copy `seed/` to a scratch
directory outside any git checkout, drop `answer.json` in it, copy `test.py` in as
`_hidden_test.py`, and run it with the scratch directory as the working directory:

    d=$(mktemp -d); cp -r slots/{ex}/seed/. "$d"/
    cp slots/{ex}/ref/answer.json "$d"/answer.json
    cp slots/{ex}/test.py "$d"/_hidden_test.py
    (cd "$d" && PYTHONUTF8=1 python3 _hidden_test.py); rm -rf "$d"
""".format(ex=ex, p=pairs[0])


def _appendix(slots, sc, ab, pairs):
    parts = ["\n## Appendix -- full output of every gate run\n"]
    for s in slots:
        parts.append("\n### `%s` -- `python3 selfcheck.py` (exit %d)\n" % (s, sc[s]["rc"]))
        parts.append("```")
        parts.append(sc[s]["out"].rstrip())
        parts.append("```")
    for p in pairs:
        parts.append("\n### `%s` -- `diff %s-noabst/prompt.md %s-abst/prompt.md`\n"
                     % (p, p, p))
        parts.append("```")
        parts.append("\n".join(ab[p]["diff"]))
        parts.append("```")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    sys.exit(main())
