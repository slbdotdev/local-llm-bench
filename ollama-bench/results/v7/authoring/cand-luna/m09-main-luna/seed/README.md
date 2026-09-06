# harrow-vane

A staged delivery pipeline. Each stage is a module under `src/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. `docs/policy-records/` - the rules that outrank both of the above.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| tenancy | `src/tenancy_flow.py` | `docs/tenancy.md` | P. Ravindran |
| quota | `src/quota_gate.py` | `docs/quota.md` | E. Thorsdottir |
| drain | `src/drain_flow.py` | `docs/drain.md` | M. Lindqvist |
| rollup | `src/rollup_flow.py` | `docs/rollup.md` | M. Lindqvist |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | K. Sorensen |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | P. Ravindran |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | L. Achterberg |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | H. Bergstrom |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | R. Okonjo |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | L. Achterberg |
| replay | `src/replay_store.py` | `docs/replay.md` | D. Ferreira |
| schema | `src/schema_gate.py` | `docs/schema.md` | E. Thorsdottir |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | P. Ravindran |
| lineage | `src/lineage_view.py` | `docs/lineage.md` | N. Oyelaran |
| audit | `src/audit_store.py` | `docs/audit.md` | N. Oyelaran |
| digest | `src/digest_view.py` | `docs/digest.md` | T. Abarca |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | A. Villanueva |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | E. Thorsdottir |
| retention | `src/retention_core.py` | `docs/retention.md` | M. Lindqvist |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy-records/`
  outranks everything else.

## Audit material

- `docs/glossary.md` - the project's own meaning for every term a newcomer would guess at.
- `docs/policy-records/` - numbered, dated rulings. A policy record outranks a component
  document, and a component document outranks a history entry.
- `data/migration-ledger.csv` - the ceiling migration's event log. It is a log and not a table
  of stages: a stage has several rows and a few stages have an attempt that was recorded and
  then annulled. Print it, resolved to one completed migration per stage, with
  `python tools/ledger_dump.py`; the resolution rule is the glossary's *counter-signature*.
