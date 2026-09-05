# NorthstarLedger

A staged delivery pipeline. Each stage is a module under `src/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. `docs/policy/` - the rules that outrank both of the above.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| quota | `src/quota_store.py` | `docs/quota.md` | J. Maldonado |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | S. Nwachukwu |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | C. Batbayar |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | P. Ravindran |
| lineage | `src/lineage_gate.py` | `docs/lineage.md` | C. Batbayar |
| retention | `src/retention_store.py` | `docs/retention.md` | M. Lindqvist |
| watermark | `src/watermark_gate.py` | `docs/watermark.md` | M. Lindqvist |
| routing | `src/routing_flow.py` | `docs/routing.md` | R. Okonjo |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | T. Abarca |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | D. Ferreira |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | K. Sorensen |
| audit | `src/audit_gate.py` | `docs/audit.md` | R. Okonjo |
| replay | `src/replay_flow.py` | `docs/replay.md` | M. Lindqvist |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | L. Achterberg |
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | P. Ravindran |
| cursor | `src/cursor_view.py` | `docs/cursor.md` | M. Lindqvist |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | L. Achterberg |
| digest | `src/digest_view.py` | `docs/digest.md` | T. Abarca |
| tenancy | `src/tenancy_flow.py` | `docs/tenancy.md` | N. Oyelaran |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | S. Nwachukwu |
| drain | `src/drain_view.py` | `docs/drain.md` | R. Okonjo |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
