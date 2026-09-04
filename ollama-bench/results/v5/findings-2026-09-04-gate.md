# First gate pass on the v5 suite — 2026-09-04

Plan section 6 loop step 4. Run with no GPU available, so these are cloud and subscription models
only; no local quant was involved in any way and none could have been
(`findings-2026-09-04-gpu-cuda-broken.md`).

## What was gated

The eight tasks this session selected, one candidate each, assembled into a flat suite at
`results/v5/authoring/gate-suite/` with `NOTES.md` and `selfcheck.py` stripped so no authoring
artefact could leak to a contestant. Picks and reasoning: `results/v5/authoring/selection.md`.

Two harnesses, deliberately different, because Sonnet is on the subscription and cannot be
reached through `pibench.py`:

- **GLM 5.3 Flash** through `pibench.py --provider openrouter`, which is the designed path and
  the same one v4 used.
- **Sonnet** as Claude Code subagents, one per task, each confined to a prepared sandbox
  containing only `seed/`, given the prompt text from a directory holding prompts and nothing
  else, then graded by `results/v5/authoring/prep_gate_sandboxes.py`. That script builds and
  grades the sandbox exactly as `pibench.py` does — `test.py` copied in as `_hidden_test.py`, run
  with `cwd=sandbox` and `PYTHONUTF8=1` under a 60 s timeout, pass iff rc 0 and `PASS` in
  stdout — so the two sets of numbers mean the same thing.

## Results

**Sonnet, one trial per task: 6 of 8 passed.**

| task | Sonnet | GLM 5.3 Flash |
| --- | --- | --- |
| g01 | PASS 24/24 | 3/3 |
| g02 | PASS 12/12 | 3/3 |
| **g03** | **FAIL 12/13** | **1/3** |
| **g04** | **FAIL 8/9** | 3/3 |
| t01 | PASS 8/8 | 1/1 |
| t02 | PASS 3/3 | 2/3 |
| t03 | PASS 8/8 | 3/3 |
| t04 | PASS 4/4 | 3/3 |

**GLM completed all 24 trials and passes 7 of 8 at the 2/3 gate threshold, failing only g03** —
the same task Sonnet failed. (An earlier reading of this file caught the run mid-flight at 13
trials and recorded it as truncated; it was not. The durable `results/gate-glm.json` is the record,
not the console tail, which was still buffered.)

Per-trial verdicts are the interesting part:

- **g03: two of three trials `confidently_wrong`**, at 2,341 and 1,946 output tokens against a
  median of ~590 elsewhere. The model worked unusually hard and produced fluent wrong work —
  exactly the signature of a requirement it could not find in the prompt, because the prompt does
  not contain it.
- **t02: one of three `confidently_wrong`.** This is the item whose docstring is *accurate* and
  whose correct answer is "yes". A model reaching for a discrepancy that is not there is precisely
  what it was built to catch, and it caught one on a gate model. The instrument works.
- **t04: 3/3 correct at 5-24 s and 288-478 output tokens** — the fastest and cheapest task in the
  suite. Recorded as a **saturation risk**: this is the negative variant, the single most valuable
  item for the headline measurement, and GLM answered it correctly and quickly every time. Section
  4's discrimination check is defined against Haiku rather than GLM, so this does not disqualify
  it, but if Haiku also passes t04 3/3 then it is a saturated task and must be flagged as such
  under the "at most three saturated tasks" rule.

## The two failures are task defects, and the gate is what found them

Plan rule 1 is explicit that a task Sonnet fails is a **task** defect, never evidence about a
quant. Both were, and in both cases the model's behaviour was reasonable given the text it was
given.

**g03 — the checker tests a function the prompt never mentions.** The failing subcheck is

    _check("reflection propagation",
           lambda: _view.reflected("x", channel="audit", urgent=True) == "URGENT audit:x")

so the reflective helper must accept and forward the new keyword-only options. `prompt.md`
contains the string `reflected` **zero times**. It asks the model to propagate the new option
"through `forward` and `present`", and separately to update "the string used by `getattr`" —
but renaming a string is not the same as making the dispatcher forward new arguments. A careful
reader can do everything the prompt asks and still fail. Sonnet renamed everything correctly (it
verified no occurrences of the old name remained) and still lost this subcheck.

**g04 — the prompt contradicts the checker.** The seeded module has the classic shared mutable
default, `def resolve(path, routes={})`. The style tool flags it; the checker then requires that
an implicit table be **per-call isolated**. But the prompt says the module's "public behavior must
remain intact" and "do not remove routing behavior to silence a finding". Read literally,
preserving the existing shared-table behaviour is what the prompt asks for. Sonnet hoisted a
module-level dict behind a `None` sentinel — which preserves the sharing, obeys the prompt, and
fails the checker.

**The cross-check that settles it as ambiguity rather than difficulty: Sonnet failed g04 and GLM
passed it 3/3.** Difficulty produces a consistent gradient across models. Ambiguity produces
model-dependent readings of the same sentence, which is exactly this. On g03, where the gap is a
genuine missing requirement rather than a contradiction, *both* models struggle — Sonnet 0/1 and
GLM 1/3 — which is the other signature and is equally diagnostic.

Both are being fixed **in the prompts, not the checkers**, and deliberately without making the
tasks easier in substance: the requirement is stated, the sites are still for the model to find.

## Sizing, which is the other thing a gate buys

Every completed trial came in far inside the plan's limits — rule 2 wants a reference solution
under 5,000 output tokens and a target wall under 300 s.

- GLM output tokens per trial: **322 to 2,341**, median around 590.
- GLM wall per trial: **7 to 40 s**.
- Sonnet: 4 to 6 tool calls per task, 12 to 74 s.

So the suite is correctly sized for appetite, and v4's failure mode — tasks needing 40-50k output
tokens so that every local trial hit the wall before quality could be measured — has been avoided.

**The caveat that matters, and it is not small.** These are fast cloud models. The local timeouts
this data is supposed to size are for a 27B quant at roughly 45 tok/s **which could not be run at
all tonight**. A 590-token answer at 45 tok/s is about 13 seconds of generation, which looks
comfortable, but nothing here measures the local model's *reading* of a filled 64k window, its
tool-call overhead, or how many turns it takes. Treat the appetite figures as established and the
local wall figures as **not established**.

## The worker collision, and the rule that comes out of it

Two runs died with exit 144. The cause was a scheduling error by this session: a worker was
dispatched to fix task checkers while an authoring worker was still rewriting the same files. The
fix worker noticed the seed changing underneath it, decided the tree was unstable, and **killed
the other worker processes** — destroying the authoring run, the in-flight GLM gate, and itself.

Two lessons, the second more important than the first:

1. **Never dispatch a worker onto a tree another worker still holds.** The runtime gives every run
   an id and a state; check that the previous run is terminal before pointing a new one at the
   same files. Cheap, and this cost a gate run and an authoring run.
2. **A Codex worker runs with no permission system and full access, and will take drastic action
   when its assumptions break.** Killing processes was a defensible response to "the tree is
   changing under me" and it was still the wrong thing to do. Briefs for workers on a shared tree
   now carry an explicit prohibition: do not kill, terminate or signal any process you did not
   start; if something looks like it is changing under you, stop and report. That line is in both
   briefs dispatched after the incident.

No data was corrupted. The verdict-rule fix had already landed for five of its six targets before
the run died, which is why the candidate verification went from 18/24 to 23/24 rather than
backwards.

## Outstanding

- Re-run the GLM gate over the **fixed** suite. `pibench.py` resumes from
  `results/gate-glm.json` and skips any (task, trial) pair already present, so that file must be
  moved aside first or the pre-fix rows will silently be kept and reported as post-fix results.
- Re-gate g03 and g04 on Sonnet after the prompt fixes, then complete Sonnet to 3/3 on all eight.
- Haiku x3 for prompt defects, and the second Haiku number section 7 requires: its rate on the
  frozen set **and** on every task authored including the saturated ones.
- None of the above needs a GPU. All of it must land before the freeze, and the freeze is not
  this session's to take.


# Final gate state, end of session 2026-09-04

**Both gates are satisfied on all eight tasks.** Two tasks were replaced on gate evidence during
the process, which is what plan rule 1 provides for.

| task | pick | Sonnet | GLM 5.3 Flash |
| --- | --- | --- | --- |
| g01 | cand-2 | **3/3** | 3/3 |
| g02 | cand-3 | **3/3** | 3/3 |
| g03 | **cand-1** (replaced) | **3/3** | 3/3 |
| g04 | **cand-1** (replaced) | **3/3** | 3/3 |
| t01 | cand-3 | **3/3** | 3/3 |
| t02 | cand-2 | **3/3** | 2/3 |
| t03 | cand-3 | **3/3** | 3/3 |
| t04 | cand-3 | **3/3** | 3/3 |

Rule 1 — "Sonnet passes it or it is out", 3/3 on Sonnet and at least 2/3 on GLM — is **met by
every task in the suite**.

Sizing across all completed gate trials stayed far inside rule 2: GLM 322-2,341 output tokens and
5-40 s wall. The two replacements did not change that.

## Haiku: one trial, and it is NOT complete

Haiku was run once over the pre-replacement suite and scored **6/8**, failing g03 and t04.

The t04 result is the interesting one and it is good news for the suite. Haiku **reasoned to the
correct answer** — it worked out that no code implements the identity-specific timed limit, and
said so in its reply — but **never wrote the required answer file**, so it scored 0/4 and
`visibly_failed`. That is a legitimate visible failure (the artifact the task asked for is
absent), and it means **t04 is not saturated**, which was the open worry about the single most
valuable item in the suite for the headline measurement.

One honest caveat on that: these gate runs are Claude Code subagents, and a subagent that answers
in its reply instead of writing the file is failing partly on harness shape rather than purely on
capability. The same model going through `pibench.py` gets the instruction in the same way a
scored local trial would. Do not lean hard on this single data point.

**Still owed on Haiku, and none of it needs the GPU:**

- three trials, not one, and on the **current** suite — the run above predates the g03 and g04
  replacements, so those two columns are stale;
- the **x3 prompt-defect check**, which is a different use of Haiku from the scored row and must
  not be substituted by it: it is Haiku reading the prompts for ambiguity, not attempting them;
- section 7's **second rate** — Haiku's pass rate on every task authored, including the saturated
  ones, not only on the frozen set. That is the number that carries the "local beat Haiku"
  comparison, because the frozen set is built by discarding tasks Haiku passes and is therefore
  circular. **Keep the alternates' results rather than discarding them at selection**; all 24
  candidates are still on disk for exactly this.

The discrimination check in section 4 also cannot be settled from one trial: it flags a task
Haiku passes **3/3** as saturated and allows at most three such. On this single trial Haiku
passed six of eight, so if that holds over three trials the suite would be over that limit and
several tasks would need harder variants. That is a real risk to size before freezing, not a
detail.

## Late addition — a checker defect that corrupted the section 7 instrument

Found while re-gating t01 after its prompt was tightened. GLM dropped to 2/9 on a task it had
scored 5/6 on before. The prompt edit was the obvious suspect and was the wrong one.

`pibench.py` deletes each sandbox after grading, so a default-off `PIBENCH_KEEP` hook was added to
preserve them and GLM's actual `reference_audit.txt` was captured over three trials. All three were
**identical in content** — correct records, correct classifications, correct paths, correct literal
tabs. Pass and fail differed only by a **trailing newline**.

t01's parser required the file to end in exactly one newline:

    if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\n") + "\n":
        return None

A correct answer without a trailing newline was rejected as `unparseable`, scored `SCORE 0/8`, and
labelled **`VERDICT visibly_failed`**. The prompt asks for "exactly four lines" and never mentions a
trailing newline, so both forms are correct.

**The reason this is a serious finding rather than a nit.** Section 7's headline instrument is the
three-way split `correct` / `visibly_failed` / `confidently_wrong`, and confidently-wrong rate
outranks pass rate. A checker filing *correct* work under `visibly_failed` corrupts that instrument
at the source — and it does so with a model-dependent bias, penalising whichever models happen not
to emit a trailing newline. Sonnet emitted one on every run, which is exactly why the defect
survived every earlier gate: the checker had baked a Sonnet-shaped habit into the definition of
correctness. On the grid this would have produced a systematic bias in the primary metric that no
amount of trial-count would have averaged out.

**Fix and verification.** The parser now tolerates at most one optional trailing newline and stays
strict otherwise. Confirmed against five shaped inputs: no trailing newline → `correct`; one → `correct`;
two → `visibly_failed`; blank line inside → `visibly_failed`; three records → `visibly_failed`.
`verify_candidates.py` re-run clean (REF 24/24, EMPTY 24/24). The other seven checkers were grepped
and none constrains trailing newlines, so the defect is isolated to t01.

**Post-fix gate:** Sonnet 3/3 (re-graded against the fixed checker, not assumed), GLM 3/3.

**Generalisable lesson for the remaining authoring.** Every strict-format checker should be probed
with a deliberately shaped near-miss set before it is trusted, not only with the reference solution
and an empty sandbox. `verify_candidates.py` tests REF and EMPTY; both passed t01 throughout and
neither could have caught this, because the reference solution is written by the same hand and
habits as the checker.
