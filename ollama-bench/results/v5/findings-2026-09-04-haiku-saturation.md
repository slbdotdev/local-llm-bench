# Haiku discrimination check and prompt-defect read — the suite is NOT freeze-ready

Plan section 4's discrimination check and its x3 prompt-defect check, run 2026-09-04. No GPU, no
local quant, no scored row. **This is section 4 gate-time evidence, not section 5's Haiku
competitive row** — that one comes after the freeze and must not be conflated with this.

## Verdict, first

**The suite must not be frozen as it stands.** Section 4 keeps a task Haiku passes 3/3 but flags
it **saturated**, and allows **at most three** saturated tasks. Five are already confirmed
saturated and two more are on track:

| task | valid trials | passes | saturated? |
| --- | --- | --- | --- |
| g01 | 0,1,2 | 3/3 | **YES** |
| g02 | 0,1,2 | 3/3 | **YES** |
| g03 | 1,2 | 2/2 | likely — needs a third trial |
| g04 | 1,2 | 2/2 | likely — needs a third trial |
| t01 | 0,1,2 | 3/3 | **YES** |
| t02 | 0,1,2 | 3/3 | **YES** |
| t03 | 0,1,2 | 3/3 | **YES** |
| t04 | 0,1,2 | 2/3 | no |

**Five confirmed against a limit of three, and plausibly seven of eight.** Trial 0 is excluded for
g03 and g04 because it predates their replacements; trials 1 and 2 were both a clean 8/8.

The only task Haiku did not pass 3/3 is **t04**, and only because on trial 0 it reasoned correctly
to "not implemented" but never wrote the required answer file. On trials 1 and 2 it passed.
So on the merits t04 is close to saturated too.

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

1. **Take the rule literally.** Five to seven tasks are saturated, the limit is three, so most of
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
