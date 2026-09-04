# pi-agent-v5 — the Phase 0 (F1/F2) agent dir

`harness_version: v5`. Use with `pibench.py --provider ollama --agent-dir <abs path to this dir>`.

## What this is a copy of

**`ollama-bench/pi-agent/`, not `results/pi-agent-v4/`.** `results/pi-agent-v4/` is the
*OpenRouter reference* agent dir (`--agent-dir` in `results/v4-ref-1800.sh`, in use by the
in-flight fp8 run); it has no ollama provider at all. The v4 **local** ladder
(`results/v4-local-ranking.sh`) passes no `--agent-dir`, so it used `pibench.py`'s default
`AGENT_DIR = <repo>/pi-agent`. That is the dir this one copies, and `pi-agent/` stays frozen as
the v4 local artefact.

## What differs from `pi-agent/`

| file | change | why |
|---|---|---|
| `models.json` | `maxTokens` 32768 -> **24576** on every ollama model (`contextWindow` untouched: 32768, or 65536 for the two `-64k` entries) | **F1**, plan section 7g, *with a revised value — see below*. With `maxTokens == contextWindow` the `Math.min` in `clampMaxTokensToContext` never binds, so pi handed the model the whole residual window as one response allowance and the 27B reasoned to the length cut with no text and no tool call. |
| `settings.json` | `compaction` `{enabled: false}` -> **`{enabled: true, reserveTokens: 8192, keepRecentTokens: 4096}`** | **F2**. `enabled: false` made `_checkCompaction` return before pi's compact-and-retry recovery for a recoverable `length` stop. The managed value `reserveTokens: 548576` must **never** be used here — at a 32k window it would compact every turn (7c.3). Invariant: `reserveTokens < contextWindow / 2`. |

Everything else (`auth.json`, `models-store.json`, provider/baseUrl/compat, retry block, shellPath)
is byte-identical to `pi-agent/`.

## F1's value is 24576, not the 8192 the plan prescribed — this was measured

The plan's F1 acceptance test ("`out_tokens` must fall below 8,300") is **falsified by the gate
runs**. Measured on `52_reengine` / `q27-Q2_K_L` / 32k:

| maxTokens | think | turns | tools | out_tokens | stopReason | result |
|---|---|---|---|---|---|---|
| 8192 | medium | 1 | 0 | 8192 | `length` | no text, no tool call — **gate fail** |
| 8192 | low | 1 | 0 | 8192 | `length` | identical — **gate fail** |
| **24576** | medium | **6** | **5** | 43218 | `toolUse` x4, `length` x2, one `compaction_end` | **gate pass** |

A direct wire probe (`results/v5-smoke-gate.probe.txt`) explains it: given 24,000 tokens of room
this quant's reasoning on this prompt **terminates** at 21,253 completion tokens. Any per-turn
allowance below that is cut mid-thought, so 8192 does not fix the v4 failure — it only makes the
same failure cheaper. The correct rule is:

> `maxTokens` must be **below** the context-clamped available room (so `Math.min` binds and the
> window is not swallowed) but **above** the model's per-turn reasoning appetite (so the turn can
> reach a tool call).

At 32k with a ~5.2k prompt the clamped available room is ~23.4k, so 24576 satisfies both. It has a
second, load-bearing effect: because `maxTokens` (24576) exceeds the clamped request (~23.4k),
`isRecoverableLength(msg, model.maxTokens)` is **true** on a length stop, which is what lets F2's
compact-and-retry fire at all. At `maxTokens: 8192` output equals the desired limit exactly, the
stop is *not* recoverable, and compaction never runs — as observed (`events: {}`).

## Comparability

Every F1-F7 change alters the measurement instrument, so **no record taken with this dir is
comparable to a v4 local record.** The v4 local ranking stands on its own terms with the
harness-cap caveat (plan section 7a) and is not re-run.

## Gate provenance

The passing gate ran from `results/pi-agent-v5-t3/`, a byte-identical copy of this dir made while
this one still held the literal-F1 value; it is kept unchanged as the artefact behind
`results/v5-smoke-gate-t3.{json,log}`.
