# halyard-mesh

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
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | K. Sorensen |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | D. Ferreira |
| reconcile | `src/reconcile_core.py` | `docs/reconcile.md` | L. Achterberg |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | R. Okonjo |
| audit | `src/audit_core.py` | `docs/audit.md` | A. Villanueva |
| digest | `src/digest_core.py` | `docs/digest.md` | P. Ravindran |
| compaction | `src/compaction_core.py` | `docs/compaction.md` | C. Batbayar |
| schema | `src/schema_core.py` | `docs/schema.md` | D. Ferreira |
| attestation | `src/attestation_store.py` | `docs/attestation.md` | S. Nwachukwu |
| quota | `src/quota_view.py` | `docs/quota.md` | D. Ferreira |
| drain | `src/drain_store.py` | `docs/drain.md` | H. Bergstrom |
| ingest | `src/ingest_flow.py` | `docs/ingest.md` | E. Thorsdottir |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | L. Achterberg |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | C. Batbayar |
| replay | `src/replay_gate.py` | `docs/replay.md` | A. Villanueva |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | K. Sorensen |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | L. Achterberg |
| retention | `src/retention_core.py` | `docs/retention.md` | M. Lindqvist |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | L. Achterberg |
| shard | `src/shard_store.py` | `docs/shard.md` | M. Lindqvist |
| routing | `src/routing_store.py` | `docs/routing.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Retirement markers

Supersession is recorded per module. The governing note is `docs/notes/` -
see SN-0418, which replaced the older SN-0311 scheme and changed what counts as a
marker. An older copy of this README described SN-0311; that description is stale
and the note itself is authoritative.
