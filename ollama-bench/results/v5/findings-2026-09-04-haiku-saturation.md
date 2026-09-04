# Haiku discrimination check and prompt-defect read — the suite is NOT freeze-ready

Plan section 4's discrimination check and its x3 prompt-defect check, run 2026-09-04. No GPU, no
local quant, no scored row. **This is section 4 gate-time evidence, not section 5's Haiku
competitive row** — that one comes after the freeze and must not be conflated with this.

## Verdict, first

**The suite must not be frozen as it stands.** Section 4 keeps a task Haiku passes 3/3 but flags
it **saturated**, and allows **at most three** saturated tasks. **Seven of the eight are now
confirmed saturated.**

> **Correction, 2026-09-04 (later in the same session).** An earlier revision of this page said
> *five confirmed, two on track*, and an intermediate correction said *six*. Both were wrong. The
> count is **seven**. Two separate errors were fixed, and both are evidenced below rather than
> asserted, so the arithmetic can be re-checked without re-running anything.

### Error 1 — g04's trial 0 was wrongly excluded

Trial 0 was excluded for *both* g03 and g04 on the belief that it predated both replacements. It
did not: g03 and g04 were replaced at different times, and trial 0 already ran g04's **current**
candidate. The evidence is the seed filenames, which differ per candidate:

- g04 candidate seeds are cand-1 `invoice.py`, cand-2 `router.py`, cand-3 `report.py`.
- `gate-haiku/trial-0/g04/` contains `invoice.py` and `check_style.py` — i.e. cand-1, the current one.
- `md5sum` agrees byte-for-byte: `gate-haiku/trial-0/g04/check_style.py` and
  `gate-suite/g04/seed/check_style.py` are both `0232a79e3b5cef2e23d23dc910110834`.

So g04 has three valid trials (0,1,2), all passes → **saturated**.

The g03 exclusion, by contrast, was *correct*: `gate-haiku/trial-0/g03/` contains
`note_bus.py note_core.py note_view.py test_notes.py` (cand-3), whereas the current cand-1 seed is
`badge_core.py badge_flow.py badge_registry.py test_badges.py`. Different task; rightly excluded.

### Error 2 — g03's third trial has now been run, and it passed

g03 was left at 2/2 "needs a third trial". That trial (`gate-haiku/trial-3`) has since been run on
the current candidate and **passed 12/12, VERDICT correct**. g03 is therefore 3/3 on trials 1,2,3
→ **saturated**.

| task | valid trials | passes | saturated? |
| --- | --- | --- | --- |
| g01 | 0,1,2 | 3/3 | **YES** |
| g02 | 0,1,2 | 3/3 | **YES** |
| g03 | 1,2,3 | 3/3 | **YES** (trial 0 excluded, cand-3 seed) |
| g04 | 0,1,2 | 3/3 | **YES** (trial 0 re-included, cand-1 seed) |
| t01 | 0,1,2 | 3/3 | **YES** |
| t02 | 0,1,2 | 3/3 | **YES** |
| t03 | 0,1,2 | 3/3 | **YES** |
| t04 | 0,1,2 | 2/3 | no |

**Seven confirmed against a limit of three.**

t04 is the only task Haiku did not pass 3/3, and its single failure is genuine rather than an
artefact of a superseded candidate: `auth.py` is byte-identical (`b74f514e977be758a019a26290a0e2f5`)
across trials 0, 1, 2 and `gate-suite/t04/seed/`, so all three trials ran the same task. On trial 0
Haiku reasoned correctly to "not implemented" but never wrote the required answer file
(`SCORE 0/4`, `VERDICT visibly_failed`, no `answer.txt` in the sandbox). On the merits t04 is close
to saturated too.

## Third condition: one-shot Haiku, no self-testing

The agentic numbers above could have been an artefact of the proxy rather than of the suite: an
agentic Haiku iterates, runs `python3`, reads checker output and repairs itself, none of which the
local arm it stands in for can do. To test that, all eight tasks were re-run with a Haiku agent
under an explicit one-pass restriction — forbidden to execute `python3` or otherwise verify its own
output before finishing (for g04, *reading* `check_style.py` was permitted, executing it was not).

**One-shot Haiku passed 8/8**, every task `VERDICT correct`, full score on each
(`gate-haiku-oneshot/trial-0/results.json`).

Compliance was verified rather than assumed: the tool-call logs of all eight one-shot runs contain
**zero** `python` or `pytest` invocations — only `find`, `grep`, `ls`, `read` and `write`. The
contrast with the agentic runs is visible in their own reports, e.g. the agentic g03 run finishes
"verified no old references remain, and test passes" (13 tool calls) while the one-shot g03 run
simply reports the edits (9 tool calls).

**This closes off the "broken proxy" explanation.** The suite is not saturated merely because the
Haiku proxy was given powers the local arm lacks; it is saturated even against a Haiku that gets
one pass and no feedback. Re-authoring harder variants is unavoidable.

These are three distinct conditions and all three belong on the page. The one-shot numbers do
**not** replace the agentic numbers — both are recorded above, and the agentic 3/3 record is what
the section 4 saturation flag is computed from.

## What that means, stated carefully

Section 4's rule exists because "a task everything passes cannot rank quants, and ranking quants
is the mission". On its face this suite fails that test badly and needs harder variants before it
is frozen.

**But the reading deserves one honest caveat, and the freezing session should weigh it rather
than take this page's headline at face value.** The Haiku used here is a Claude Code subagent with
full agentic tooling: it reads files, writes files, and runs `python3` to check its own work,
iterating until satisfied. That is a substantially stronger configuration than a plain reference
completion, and much stronger than the local arm — a 3-bit 27B quant at 48k of filled context, at
~45 tok/s, under a 900 s wall. It is entirely possible for a task to be saturated for
agentic-Haiku and still discriminate sharply among local quants, which is the comparison the
benchmark actually cares about.

Two readings follow, and they lead to different actions:

1. **Take the rule literally.** Seven tasks are saturated, the limit is three, so most of
   the suite needs replacing with harder variants before the freeze. Safe, faithful to the
   predeclared rule, and expensive — it means another authoring round.
2. **Treat the rule's proxy as broken here** and note that the check was designed against a
   weaker Haiku configuration than the one available. Then the honest move is to re-run this check
   in a configuration comparable to the local arm (no iterative self-testing), or to accept the
   saturation and report it prominently as a limitation of the ranking.

**This session does not choose between them: it is a structural decision about what the suite
measures, and section 6 says those get banked, not taken.** The evidence is here; the choice
belongs with the session that freezes. What must not happen is freezing silently as though the
check had passed.

Section 7 already anticipates part of this, and its wording is now doubly important: Haiku's rate
must be reported **on the frozen set and on every task authored including the saturated ones**,
with the second number carrying the comparison, precisely because a set built by discarding tasks
Haiku passes is circular. All 24 candidates remain on disk so the unfiltered number is still
computable — **do not discard the alternates.**

## The x3 prompt-defect check

Three independent Haiku readers were given the eight prompts and asked only to find ambiguity —
places where a competent reader could reasonably do the wrong thing through no fault of their own
— and explicitly told not to report a task as ambiguous merely for being hard. They did not
attempt the tasks. Results:

| reader | finding |
| --- | --- |
| 1 | **t01 ambiguous** — the worked example shows single-slash paths while the path actually in play is double-slash (`//infra/handbook/oncall.md`), so whether the replacement should preserve or normalise the double slash is unclear. Weakest prompt: t01. |
| 2 | **t04 ambiguous** — the prompt demands "the smallest contiguous line span containing the implementation itself", which has no correct answer if an implementation is split across non-contiguous sections. Weakest prompt: t04. |
| 3 | **t01 ambiguous** — "standalone occurrence" is used repeatedly and never defined; whether occurrences inside code fences, quotations or comments count is left to inference. Weakest prompt: t01. |

All three read g01-g04, t02 and t03 as CLEAR.

**t01 was flagged by two of three readers, on two different grounds**, and both are real: the
double-slash/single-slash mismatch is checkable against the prompt, and "standalone" genuinely is
undefined. t01 should be tightened before the freeze — define "standalone occurrence" explicitly
and make the example use the same path shape as the material.

**t04's flag is narrower but sound as a latent hazard.** It does not bite the current candidate,
whose correct answer is "not implemented" and which therefore never needs a span at all; it would
bite a positive variant with a split implementation. Worth a sentence in the prompt saying what to
cite when an implementation is not contiguous, if a positive t04 variant is ever used.

Neither finding invalidates a gate result already recorded: every task passed Sonnet 3/3 and GLM
>=2/3 with these prompts as they stand.

## Method note

Three readers rather than one, because a single reader reporting "CLEAR" everywhere is
indistinguishable from a reader that did not look. Two of the three found something, they found
*different* things, and the two that agreed agreed on the same task by different routes — which is
about the strongest signal this kind of check can give.

## Fourth and fifth conditions: Haiku at 48k requested fill

Every condition above ran against an **unpadded** sandbox, roughly 2k of material — a configuration
the grid never runs. Since the grid runs these same tasks at 24k-64k of fill, section 4's
discrimination check had never been applied to the axis the benchmark actually measures. Two more
rows were run to close that, one trial across all eight tasks, agentic Haiku, comparable to trials
0-3.

**Both rows: 8/8, every task `VERDICT correct`.**

| condition | requested fill | result | median achieved fill |
| --- | --- | --- | --- |
| agentic, unpadded (trials 0-2) | none | 7 of 8 saturated | 18,603 |
| one-shot, unpadded | none | 8/8 | 18,603 |
| agentic, 48k **excludable** filler | 48,000 | 8/8 | 21,643 |
| agentic, 48k **non-excludable** filler | 48,000 | 8/8 | 22,669 |

Achieved fill is the model's own reported prompt token count, not the padding written.

**How much these two rows are worth, stated carefully.** The first 48k row used filler that was
trivially excludable by filename and location, so it largely re-measures the unpadded condition and
is **inconclusive on the padding axis**; the interpretation was fixed in advance and it is not
citable as having closed the fill question. The padding was then fixed — realistic names,
interleaved into the seed's own directories — and the row re-run once. That second row is the
meaningful one.

**But neither row tests 48k of context pressure, and that limitation is the real result.** Against
~48,000 tokens of material written per task, median achieved fill was 22,669 against an unpadded
floor of 18,603, so padding contributed roughly 4,100 tokens — under 10% of what was written.
Padding on disk only enters the context if the model reads it, and an agentic arm reads the two or
three files it needs. (t04 is the exception at 37,555 tokens over 32 tool calls, because answering
its negative question honestly requires searching the tree — difficulty drove the reading, not the
padding.) Details in `findings-2026-09-04-grid-harness-gap.md`.

**So the honest statement is:** saturation holds at roughly 22k of achieved fill with realistic,
non-excludable filler present in the tree. **Saturation at a genuine 48k+ of context occupancy
remains untested**, and cannot be tested by writing filler to disk. It is not evidence either way
for the two readings; it removes one objection to the literal reading without settling it.

This does not change the count: **seven of eight tasks saturated against a limit of three**, on
every condition tried — unpadded agentic, unpadded one-shot, and both padded rows.

## Sixth and seventh conditions: Haiku AND Sonnet at genuine prompt fill

Every earlier condition ran at 2k-22k of achieved context, and the disk-padding mechanism that
produced those numbers has since been replaced by prompt-side fill. So the discrimination check was
re-run at real fill, and — the Sonnet budget restriction having been lifted for the night — paired
with a Sonnet row at identical fill. Same eight tasks, same composed prompts (instruction verbatim
and first, further context after), one trial each.

| condition | achieved context (median) | range | result |
| --- | --- | --- | --- |
| Haiku, unpadded | 18,603 | 17,747-23,604 | 8/8 |
| Haiku, old disk padding | 22,669 | 20,847-37,555 | 8/8 |
| **Haiku, prompt-side fill** | **49,210** | **41,721-53,978** | **8/8** |
| **Sonnet, prompt-side fill** | **62,656** | **50,638-67,158** | **8/8** |

**The fill is real this time** — median achieved context rose from 18.6k to 49.2k on the same arm,
and every task is now being answered under roughly 2.6x the context load of the original check.

**Haiku still passes 8/8. The saturation count is unchanged at seven of eight.** The suite is
saturated against Haiku at unpadded, one-shot, disk-padded and genuinely-filled conditions alike.
The "it was only saturated because the context was empty" objection is now closed the same way the
"broken proxy" objection was.

**Sonnet also passes 8/8 at ~62.7k median context**, which is the useful control: it says the fill
is not quietly breaking the tasks for everyone, so Haiku's 8/8 is about task difficulty rather than
about the harness. It does *not* say the fill is costless — see the limitation below.

### A limitation of the filler, recorded because it bounds what these rows prove

Several Sonnet runs identified the added material as filler unprompted — "unrelated filler",
"distractor/decoy material from a different fabricated codebase", "boilerplate record-filtering
decoys". The material is realistic in *form* (plausible module and document names, ordinary-looking
code and notes) but generic in *content*, so a strong model recognises it as not-this-project and
sets it aside cheaply.

That does not undermine the fill mechanism, whose job is occupancy, and occupancy is measured and
achieved. But it bounds the claim: **these rows show the tasks survive a large volume of
recognisably irrelevant context, not that they survive plausible-but-wrong material that has to be
disambiguated.** The harder axis — filler drawn from the same project as the answer, so that
judging relevance is itself the work — is not tested here and would be a different and probably
sharper instrument. Noted for the owner; not changed, because changing it now would alter what the
saturation rows mean mid-measurement.
