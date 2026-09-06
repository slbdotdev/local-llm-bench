# NOTES — n05-main-luna (behaviour 9, rung 0)

## 1. Failure mode

Mode 9 in the round brief's slot table is the non-lexical join task: the model must compute an
opaque key before searching for the record it addresses.  It measures whether a model can carry
an arithmetic join across human labels, a prose rule, and two artifact kinds.

## 2. Distinguishing condition

A model that relies on lexical retrieval or directory order will search the allocation records
directly, pair them with the manifest order, or use an ordinal as if it were already a key.  The
material rules this out: the policy says the key is the product of the per-stage ordinal and
offset, and decision records contain no human labels.  `facts()` measured 19 unique
four-digit keys and one record per stage; the positive answer is `audit`, `compaction`, `cursor`, `rollup`.

## 3. Why the grader is sound

The grader independently checks existence, UTF-8 readability, exact key order, the stage set,
the count, the formula, and seed integrity/scope.  The set is compared order-insensitively and
the count numerically, while the prompt leaves whitespace unspecified.  Two complete wrong
answers are probed: filename-order pairing and ordinal-only searching.  An untouched workspace
is visibly_failed.  The five whitespace perturbations remain correct.

## 4. Positive or negative

Positive: the report names the stages whose computed records say `reroute`.

## 5. Rung 0 and material necessity

The answer is not stored in one file and no file maps labels to keys.  Every stage document is
needed for its ordinal, every module for its offset, every allocation record for its disposition,
and the policy is needed for the multiplication rule.  The prompt names only the complete roster
pointer, `config/manifest.json`, which is declared `named_in_prompt`; it does not name an answer
holder.  The sweep covers 21704 of 30249 measured seed tokens (71.8%), so the
generated repository is necessary context rather than prompt decoration.  No prompt word
selectively assembles the eight declared load-bearing paths.

## 6. Load-bearing paths

The declaration has 8 paths across 5 causal hops:

- `docs/architecture/allocation-keys.md` — states the canonical multiplication rule and rejects positional matching (*rule*)
- `config/manifest.json` — the complete roster of human-labeled stages in scope (*enumeration*)
- `docs/compaction.md` — the human-labeled stage's deployment ordinal (*ordinal*)
- `src/parcel/compaction_view.py` — the same stage's region offset (*offset*)
- `ops/allocation-records/allocation-1548.md` — the decision reached only through that computed key (*decision*)
- `docs/rollup.md` — the human-labeled stage's deployment ordinal (*ordinal*)
- `src/parcel/rollup_core.py` — the same stage's region offset (*offset*)
- `ops/allocation-records/allocation-2100.md` — the decision reached only through that computed key (*decision*)

## 7. Near-miss table

| outcome | result |
| --- | --- |
| reference | correct, full score |
| untouched sandbox | visibly_failed, no traceback |
| filename-order pairing | confidently_wrong |
| ordinal-only search | confidently_wrong |
| swapped key order | confidently_wrong |
| no trailing newline | correct, full score |
| two trailing newlines | correct, full score |
| CRLF line endings | correct, full score |
| one leading blank line | correct, full score |
| trailing spaces | correct, full score |

## 8. Derivability

The reference is derived from `seed/` by multiplying each document's ordinal by its module's
offset, opening the computed record, and reading its disposition; the formula is read from the
policy.  No expected label, count, or key is typed into the reference.
