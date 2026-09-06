# latchbridge

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
| dispatch | `src/dispatch_view.py` | `docs/dispatch.md` | N. Oyelaran |
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | E. Thorsdottir |
| retention | `src/retention_core.py` | `docs/retention.md` | L. Achterberg |
| routing | `src/routing_flow.py` | `docs/routing.md` | H. Bergstrom |
| audit | `src/audit_view.py` | `docs/audit.md` | M. Lindqvist |
| reconcile | `src/reconcile_store.py` | `docs/reconcile.md` | J. Maldonado |
| watermark | `src/watermark_view.py` | `docs/watermark.md` | P. Ravindran |
| throttle | `src/throttle_store.py` | `docs/throttle.md` | D. Ferreira |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | J. Maldonado |
| cursor | `src/cursor_store.py` | `docs/cursor.md` | K. Sorensen |
| shard | `src/shard_view.py` | `docs/shard.md` | R. Okonjo |
| tenancy | `src/tenancy_flow.py` | `docs/tenancy.md` | P. Ravindran |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | R. Okonjo |
| attestation | `src/attestation_core.py` | `docs/attestation.md` | L. Achterberg |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Release gate

Releases are gated by the checklist under `docs/`: run the verification it names, note
whether it passes or fails, and report what it actually printed, not what an earlier note
claims. Intake journals under
`data/intake/` are regenerated fixtures (see `tools/make_fixtures.py`); they are
evidence, not configuration, and are never edited by hand.
