# NOTES — n03-main-luna (behaviour 5, rung 0)

## 1. Failure mode

Mode 5, documentation that disagrees with the code, extended to a three-way disagreement with
a prose tiebreak. It measures whether a model can organize conflicting evidence by the stated
source-of-truth rule instead of selecting the newest, most familiar, or most operationally
plausible artifact.

The public design shape is a three-source precedence reconciliation, used here only as design
inspiration. The data and wording are ordinary capacity-review material authored for this
project.

## 2. Distinguishing condition

Each stage has at least two different `handoff_capacity` values. The markdown component document,
Python module constant, and CSV migration row each carry a possible value, and the CSV row alone
carries the neutral resolution class. The in-force engineering record says which source wins for
each class and how to fall back when one is absent. A model that follows artifact plausibility
instead of the record will commonly choose the document for all stages, the module for all
stages, or the latest migration value for all stages. The material rules those courses out by
stating the three class-specific orders and that the slate order is an exception only for
`handoff_capacity`.

The neutral classes occur 7, 6, and 6 times respectively among
19 stages. Missing per-stage records are document=4, module=6, and
migration-ledger=4. The final answer is positive: it reports one selected value and
source for every stage.

## 3. Why the grader is sound

There are eight independent subchecks: the deliverable exists, is readable as UTF-8, and has
the four keys in the stated order and shape; then one group checks all selected capacities, one
checks all selected sources, one checks their total, and one checks the artifact governing the
exception. The integrity/scope check keeps every seed file unchanged and rejects any unrelated
file. A wrong precedence rule is a complete, well-formed report but fails the relevant value,
source, and total groups, so it is `confidently_wrong` rather than visibly incomplete.

The reference is generated from the seed after the overlay. It reads each available per-stage
prose figure, module constant, and ledger value, parses the three precedence sentences and
fallback rule from the record, and asserts that available values differ and that class counts
are balanced. The total is computed by summing the selected values. No report value is asserted
from a fact absent from the seed.

## 4. Rung 0: why the material is necessary

No seed file holds the answer. The record gives only the precedence rules; the ledger gives the
stage roster rows, class, and a possible value; each component document gives a possible second
value; and each module gives a possible third value. The output combines the winning available
value and source for every stage and then sums them. The values are hash-derived and intentionally
different; the fresh module constants are not echoed into any index, history, test, or summary
artifact; `r3/check_index_leak.py` verifies the module constant appears only in its own stage
module.

The prompt gives the scope as every stage in the current manifest, which is the one legitimate
roster pointer and is declared `named_in_prompt` in `LOAD_BEARING`. It names no answer-bearing
path and no value. A selective grep over prompt vocabulary cannot assemble the answer because
the three values use different artifact-specific names and the class-to-source mapping is prose.

The sweep covers 21518 of 30090 measured material tokens (71.5%): the
engineering record, migration ledger, manifest roster, and every stage document and module.
That traversal is necessary because the selected source depends on each row's neutral class and
available records, and the report must aggregate all stages.

## 5. Load-bearing table

`test.py` declares 9 load-bearing paths across 4 causal hops; the acceptance gate
requires at least six paths and three hops, and must touch at least five paths.

- `docs/engineering/capacity-resolution.md` — the engineering record states the prose tiebreak for all three classes (*precedence*)
- `data/handoff-capacity-ledger.csv` — one migration row per stage carries the class and a possible ledger value (*enumeration*)
- `config/manifest.json` — the repository's current roster defines the stages in scope (*enumeration*)
- `docs/cursor.md` — the component document's handoff capacity for cursor (*document-value*)
- `src/cinder/ingest_store.py` — the Python module's handoff capacity for ingest (*module-value*)
- `docs/lineage.md` — the component document's handoff capacity for lineage (*document-value*)
- `src/cinder/lineage_core.py` — the Python module's handoff capacity for lineage (*module-value*)
- `docs/digest.md` — the component document's handoff capacity for digest (*document-value*)
- `src/cinder/attestation_gate.py` — the Python module's handoff capacity for attestation (*module-value*)

## 6. Near-miss table

The reference scores 8/8 with `PASS` and `VERDICT correct`. The untouched sandbox is
`visibly_failed` without a traceback. Three complete but wrong answers — document, module, or
migration row preferred for every class — are `confidently_wrong`. The swapped key order is also
`confidently_wrong`. No scope-forbidden near-miss is applicable to mode 5.

All five unspecified formatting perturbations pass 8/8 and remain `correct`: no trailing
newline, two trailing newlines, CRLF, one leading blank line, and trailing spaces. The prompt
fixes key order and pair order, so those order changes are intentionally not formatting
perturbations and fail.

## 7. Budget and derivability

This is not mode 8. The reference is 815 characters and is under the output limit. Every
value it asserts is derived from seed files: the available per-stage values from the three
artifact kinds, the winning source from the three rule sentences, each row's class, and fallback
availability, the total from those winners, and the exception artifact from the record's explicit
exception paragraph.
