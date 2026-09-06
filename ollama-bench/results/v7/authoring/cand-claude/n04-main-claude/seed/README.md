# pellworth-array

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
| attestation | `src/attestation_core.py` | `docs/attestation.md` | H. Bergstrom |
| digest | `src/digest_view.py` | `docs/digest.md` | E. Thorsdottir |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | R. Okonjo |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | L. Achterberg |
| quota | `src/quota_gate.py` | `docs/quota.md` | M. Lindqvist |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | P. Ravindran |
| drain | `src/drain_view.py` | `docs/drain.md` | R. Okonjo |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | H. Bergstrom |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | L. Achterberg |
| ledger | `src/ledger_flow.py` | `docs/ledger.md` | A. Villanueva |
| schema | `src/schema_gate.py` | `docs/schema.md` | C. Batbayar |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | A. Villanueva |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | S. Nwachukwu |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | K. Sorensen |
| shard | `src/shard_core.py` | `docs/shard.md` | D. Ferreira |
| tenancy | `src/tenancy_store.py` | `docs/tenancy.md` | R. Okonjo |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Operational records

- `ops/journal/` - the depth change journal, one file per change request. It is an
  append-only record of amendments to the vaults' retained depths, it is not a table of
  current values, and its entries are numbered journal-wide rather than per file.
- `docs/journal-protocol.md` - what each kind of journal entry means, and the order the
  journal is read in. It is the only place those rules are written down.
- `docs/capacity-note-2035-02.md` - a point-in-time reading of five vaults, kept because the
  array refresh model cites it. It is not maintained; see the note's own first paragraph.

Each stage's own document has a *Retained depth* section naming the evidence vault that stage
writes into. The depth a stage was commissioned with is a constant in the stage's module. The
depth in force is that constant as the journal has since amended it, and is deliberately
written down nowhere.
