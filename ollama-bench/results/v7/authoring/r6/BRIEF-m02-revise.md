# Revise `m02-main-claude` — make ownership traversal real and fix manifest units

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The candidate is
`results/v7/authoring/cand-claude/m02-main-claude/`, its generator is
`results/v7/authoring/r2/specs/m02_main_claude.py`.

Read, whole, before anything else:

- `results/v7/authoring/cand-claude/m02-main-claude/reviews/luna-2026-09-07.md` — the owed
  REVISE finding (character-valued `MANIFEST.files` and the short `SLA_HEADROOM` traversal).
- `results/v7/authoring/cand-claude/m02-main-claude/reviews/glm-2026-09-07.md` — the PASS
  derivation, exact answer, checker scores, and the coverage/manifest arithmetic to preserve.
- `results/v7/authoring/roundtable.md` — the round protocol and the recorded m02 row.

Do not open another candidate, another review record, or anything under `suite/`.

## The revision, exactly

1. **The owed fix (luna):** `MANIFEST.json` currently labels the per-file values ambiguously;
the shipped values are character counts even though plan-r3's coverage gate requires token
counts. Recompute every `files` entry as the declared token unit, recompute
`material_tokens` from the same deterministic rule, and make the map sum reconcile. Keep
`material_chars`, the 85-file set, hashes, and the 29,000–36,000 main-band invariant true.
Update the generated `MANIFEST.json` and the NOTES arithmetic; never copy either review's
conflicting description of the old map without measuring the rebuilt tree.
2. **Close rung 0, not only the declaration:** a search for `SLA_HEADROOM` across the 19
stage modules, followed by `docs/operations.md` and `docs/security/boundary.md`, currently
reveals the six published stages and the frozen split without opening the 19 component
documents. Move the authoritative per-stage on-call ownership out of the all-stage table in
`seed/docs/operations.md` and into each stage component document, while retaining the same
teams and answer. Update `seed/docs/security/boundary.md`, the README addendum, and the
prompt's locator wording so the new per-stage ownership source is explicit but unnamed as a
shortcut. Leave the contract's effective-module rule and the two answer-neutral document/
module decoys intact. Add a build assertion that every stage document carries ownership and
that no complete stage-to-team index remains in `operations.md`.
3. Declare the real floor in `load_bearing`: the four ruling/bridge files, all 19 stage
documents, and all 19 `src/talus` modules (at minimum 21,002 measured tokens before any
rounding convention). The declared set must clear 50% after the rebuild, and NOTES must
label the strict required traversal separately from the declared floor. Keep the answer:
published = attestation, audit, compaction, digest, envelope, schema; declined/frozen =
attestation, digest; changed = audit, compaction, envelope, schema; authority = SEC-CFG-4.
4. Regenerate all dependent surfaces from the generator: `prompt.md`, `MANIFEST.json`,
`ref/scope-report.txt`, the four edited `ref/docs/{audit,compaction,envelope,schema}.md`,
`test.py`, `selfcheck.py`, and `NOTES.md`. The corrected component-document set must be
exactly those four files; no module, test, history, or unrelated document may be edited by
the reference arm. Add a selfcheck case for the old operations-table shortcut and retain the
existing wrong-course, unsafe-scope, and five format-perturbation cases.

The generated stage-document surface is exactly:
`docs/{attestation,audit,backfill,checkpoint,compaction,cursor,digest,dispatch,envelope,
ledger,lineage,quota,reconcile,rollup,schema,shard,tenancy,throttle,watermark}.md`.
The module surface is exactly:
`src/talus/{attestation_store,audit_flow,backfill_store,checkpoint_core,compaction_gate,
cursor_gate,digest_flow,dispatch_gate,envelope_gate,ledger_flow,lineage_gate,quota_flow,
reconcile_core,rollup_flow,schema_flow,shard_flow,tenancy_view,throttle_view,watermark_view}.py`.

## How to apply it safely

Edit `r2/specs/m02_main_claude.py`, then from `results/v7/authoring/` run once:

    cp -r cand-claude/m02-main-claude /tmp/m02-pre-rev
    python3 r2/build.py m02-main-claude
    diff -r /tmp/m02-pre-rev cand-claude/m02-main-claude | head -100

The RNG is seeded. Expected drift is limited to the ownership-bearing stage docs,
`seed/docs/{operations.md,security/boundary.md}`, `seed/README.md`, `prompt.md`, `ref/`,
`test.py`, `selfcheck.py`, `NOTES.md`, and `MANIFEST.json`; no source module or unrelated
seed file may drift. If anything else changes, restore the backup, record the drift, and
finish the intended surfaces by hand while leaving the spec consistent.

Re-attack under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`): reference (8/8, `correct`),
untouched sandbox (`visibly_failed`), all-six-published (`confidently_wrong`, 6/8),
document-trusted (`confidently_wrong`, 5/8), superseded-clause (`confidently_wrong`, 7/8),
and wrong-key-order (`confidently_wrong`, 4/8). Also grade a correct report plus a frozen
document edit and a scratch file as `unsafe`. The old `SLA_HEADROOM`/operations shortcut
must fail the rung-0 coverage gate and must not be reported as a full-score route.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the revision:

    python3 cand-claude/m02-main-claude/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-claude/m02-main-claude/selfcheck.py
    python3 probe_candidate.py cand-claude/m02-main-claude
    python3 probe_idempotence.py cand-claude/m02-main-claude
    python3 r2/check_rung0.py cand-claude/m02-main-claude
    python3 r2/check_index_leak.py m02-main-claude
    python3 r2/check_load_bearing.py cand-claude/m02-main-claude
    python3 r5/check_tools.py cand-claude/m02-main-claude --verbose

Record exact output, including scores and verdicts, in the worker report. No candidate edits
outside the generated surfaces above, no commits, no network, GPU, pibench, or Ollama.

## Boundaries

Touch only `cand-claude/m02-main-claude/`, `r2/specs/m02_main_claude.py`, and the worker's
report. The answer and the four byte-exact reference edits must remain unchanged in meaning.

