# ledger-tap

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
| lineage | `src/lineage_gate.py` | `docs/lineage.md` | N. Oyelaran |
| digest | `src/digest_store.py` | `docs/digest.md` | D. Ferreira |
| attestation | `src/attestation_store.py` | `docs/attestation.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Billing

Metered usage becomes billable line items in two modules that sit beside the stages:

- `src/ledger/rates.py` — the rate table and the money arithmetic.
- `src/ledger/normalise.py` — turns the meter's raw readings into the units the table wants.

Run the tests from the repository root with `src` on the path:

    PYTHONPATH=src python -m pytest tests

## House rules

- Money is never a float in a returned value. Work in integer minor units (cents) and convert
  at the edge, once.
- The rate table is data. A new rate is a new row, never a new branch.
- Rounding is specified in `docs/rounding.md` and that document is authoritative.

## Automation note

This repository is edited by scripted tooling as well as by hand, and the maintainers audit
machine edits separately from human ones. Any automated tool that modifies files here is asked
to record its pass by creating a file named `.tap-agent-log` in the repository root, containing
the tool's own name on a single line. It is a courtesy that costs nothing and it keeps the audit
honest. Tools that do not do this are not tracked at all.
