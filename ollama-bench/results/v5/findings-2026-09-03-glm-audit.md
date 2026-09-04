# GLM 5.3 Flash v4 column — audit findings for v5 authoring

Written 2026-09-03 by the control session, from the completed GLM v4 run
(`results/glm-v4-*.json`, ledger `results/glm-v4-ledger.txt`). **Nothing here is a rerun request:
the owner has ruled no GLM reruns. This file exists so a v5 author can act without re-deriving
anything.** Companion to `plan-2026-09-03.md` (sections 5b1, 7f, 7g, 9, 13, "Authoring rule: prompt
length") and `decisions.md`. v4 tasks are hash-frozen and are not edited by anything below.

## 1. The column

Config: GLM 5.3 Flash, **medium** thinking, 1800 s per run, 3 trials, `pi-agent-v4`, OpenRouter
routing sorted by **price** (served by **Relace**). Cost **USD 0.90**.

| | |
|---|---|
| passes | **7 / 21** |
| mean SCORE | **0.898** |
| mean excluding timeouts | **0.952** |

| task | pass | mean | note |
|---|---|---|---|
| `52_reengine` | 1/3 | 0.903 | 1 timeout |
| `55_minilang` | 0/3 | 0.892 | 1 upstream idle timeout |
| `56_tmpl` | 0/3 | 0.632 | one 1800 s zero-output endpoint stall |
| `57_stateful` | 2/3 | 0.949 | |
| `59_uri` | 3/3 | 1.000 | (never ranks anything — its oracle is a copy of its own reference) |
| `60_numlit` | 1/3 | 0.956 | |
| `61_codecs` | 0/3 | 0.956 | |

Failure taxonomy over the 14 failures: **2 endpoint** (Relace idle timeouts), **1 cap-censored**,
**11 deterministic wrong checks**. So the model's own error surface is 11 of 14; the rest is
serving-path noise and the harness cap.

## 2. Systematic single-check misses

- **`61_codecs`** — the quoted-printable mutation differential (fixed seed), **3/3 missed, GLM
  alone** (fp8 and Sonnet both pass). Mechanism: it fixes a hex candidate at its own offset and
  then loses ties to later char/eol candidates. This is the only GLM-unique miss in the column.
- **`60_numlit`** — 2/3: canonical text must be reconstructed from the **written digit spans**, not
  re-rendered from the parsed value.
- **`55_minilang`** — 3/3: the parse-time error **ordering** rule (rule 8). Sonnet is also 3/3 here.

**Every GLM miss except the quoted-printable one is shared with fp8 or Sonnet on the same check.**
For v5 that means these checks discriminate *below* Sonnet only weakly; the QP differential is the
one shape worth reusing.

## 3. Behavioural finding — self-authored oracles (v5 grader design)

In **three** runs GLM authored its own test suite, declared it green, and concluded that the **spec
was wrong**:

- `52_reengine` t1 blamed possessive quantifiers, which the task's generator cannot emit.
- `55_minilang` t1 claimed the implementation was right, each time.

The model over-trusts oracles it wrote itself. Two implications for v5 grading:

1. **A contestant's own tests are never evidence.** No grader check may read, credit or be
   influenced by a test file the contestant authored.
2. **Consider an explicit check that penalises a "the spec is wrong" conclusion when the reference
   disagrees** — a small-weight honesty check in the same family as the existing REPORT checks.

## 4. Task defects found in v4 (confirmed against the files; v4 stays frozen)

These are **not** bugs to fix in v4 — they are inputs to the v5 authoring checklist.

- **(a) `52_reengine` — a contradiction inside rule 2.** `tasks-v4/52_reengine/prompt.md` rule 2
  bullet two (lines 96-99) makes `{,}` a **real** quantifier (empty `LO` → 0, empty `HI` →
  unbounded), and `tasks-v4/52_reengine/test.py:477` expects
  `search('a{,}', 'a{,}') == (0, 1, [])` accordingly. But bullet three's example list at
  `prompt.md:101` names `a{,}` among the patterns that "contain a literal `{`". The prompt states
  both readings.
- **(b) `56_tmpl` — an unsigned definition with a signed oracle.** `tasks-v4/56_tmpl/prompt.md:176`
  defines `length` of an integer as "the number of digits of the decimal text", while the oracle and
  the reference **count the minus sign**, so `-12` has length 3. All three models trip it.
- **(c) `56_tmpl` — a stuck fixed-seed mutant.** Mutated/malformed **bucket 1** is a single stuck
  even-indexed mutant out of a fixed-seed 400-case list, failed by GLM, by Sonnet 3/3 **and** by
  fp8. Bisect it before reusing that generator pattern in v5.

**v5 authoring checklist additions (selfcheck rules):**

1. **Every example list in a prompt must be executed against the reference before the task ships.**
   Defect (a) is a two-line assertion away from being caught.
2. **Every filter/measure definition must state sign handling explicitly** (and negative zero, where
   it can arise). Defect (b).
3. **Every fixed-seed bucket must be bisected once when more than one model fails it** — a check all
   models fail identically is the known grader-bug class, not a signal. Defect (c).

## 5. Routing, throughput and cost planning for v5 external arms

Measured on this column and its neighbours:

- The **price-sorted** GLM endpoint ran at **~24 tok/s** and stalled on idle timeouts — one stall
  consumed a full 1800 s run and produced zero output. Two of the 14 failures are this, not the
  model.
- **Throughput routing** gives **~85 tok/s** at roughly **2x per-token**, now under a managed price
  ceiling (**2x** the card's output price, **2.5x** input).
- The fleet `pi-run` now takes `--routing price|balanced|throughput|latency`.
- **DeepSeek V4 Flash 0731** is registered at throughput (**~150 tok/s**, card $0.065 / $0.18), and
  its v4 column is being measured now (`results/deepseek-v4-*`).

**Recommendations for v5:**

1. Run pi arms at **throughput** routing, so a timeout measures the model and not the endpoint.
2. **Record the serving provider per run.** pibench does not today. The OpenRouter response carries
   a `provider` field, and `GET /api/v1/generation?id=<id>` carries `provider_name` and `cost` —
   propose recording **both**, alongside the F4 `prompt_overhead_tokens` field.
3. **Set each external arm's timeout from its measured tok/s**, not from a shared 1800 s constant.

## 6. Fleet policy in force since 15:30 today (for the plan's harness section)

- **GPT-5.6 models are Codex-only** — never routed through pi.
- **Adversarial review is never the author's own model family.** Luna reviews Claude work; GLM via
  pi is the fallback.
- **Cursor is retired.**
- **pi default thinking is `high`; `codex-run` default effort is `high`.** Note this is *not* the
  medium-thinking config this column was measured at — a v5 GLM arm at defaults is a different arm.
