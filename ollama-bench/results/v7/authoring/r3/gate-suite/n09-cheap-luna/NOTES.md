# NOTES — n09-cheap-luna (behaviour 5, rung 0)

## 1. Failure mode

Mode 5, documentation that disagrees with the current project state, used here to measure
premature commitment. The first release summary is complete, coherent and correctly shaped,
but a later dated correction changes two dependent report fields.

## 2. Distinguishing condition

The stale summary names audit, ingest, checkpoint, attestation, throttle; those candidate rows total 566. The dated
entry removes audit from the current release set. A solver that stops at the first
complete-looking answer will therefore get exactly the two unchanged fields right and the
stage list and total wrong. The material makes the update explicit and dated; there is no
judgement call.

The decisive per-stage datum is release_status, written once into each component document by the
overlay. It is not echoed by the manifest, indexes, history entries or tests, and no summary
file carries the per-stage capacity values. This is a document row rather than a per-stage
module constant, so DECISIVE_CONSTANT is intentionally not declared. The answer requires
traversing the roster and all component records, then applying the later update.

## 3. Rung 0 and sweep

The prompt names only the deliverable and the project manifest's legitimate roster pointer;
it does not name the summary, changelog, or component-document paths. No file contains the
correct four values together: the summary contains the pre-correction pair, while the
component records and correction must be reconciled. The expected sweep is 9563 of
13004 measured material tokens (73.5%), within the intended 60-80% traversal range.
The modules corresponding to candidate component records are included because each record
points to its implementation and the maintenance sweep verifies that association. Tests and
deferred-stage modules are coherent project context but do not carry the release property and
are not counted in the expected sweep.

## 4. Grader soundness

The grader checks deliverable existence, UTF-8 readability, exact key shape/order, four
independent values, and seed integrity/scope. The four groups separate the two fields changed
by the correction from the two fields that remain unchanged. The stale summary is a complete
wrong-but-plausible answer and scores 6/8; keeping its capacity with the corrected stage list
scores 7/8. An untouched sandbox is visibly_failed. No edit perturbation is legitimate.

## 5. Positive or negative

Positive: at least one stage remains in the corrected release set, so an untouched empty report
cannot pass by luck.

## 6. Load-bearing declaration

- config/manifest.json — the complete roster and its declared order (enumeration)
- docs/release-summary.md — the first complete release answer a reader is expected to find (draft)
- history/CHANGELOG.md — the later dated line that removes one candidate (correction)
- docs/audit.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/schema.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/ingest.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/checkpoint.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/rollup.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/attestation.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/throttle.md — the component's release eligibility and reserved capacity (dependent-values)
- docs/reconcile.md — the component's release eligibility and reserved capacity (dependent-values)

The declaration has 11 paths across 4 causal hops; the correction is one
hop, and the per-stage records are the dependent-values hop for the two changed keys.

## 7. Near-miss table

| case | expected result |
| --- | --- |
| reference | correct, 8/8 |
| untouched sandbox | visibly_failed |
| complete earlier summary | confidently_wrong, 6/8 |
| corrected stages with stale capacity | confidently_wrong, 7/8 |
| keys in wrong order | confidently_wrong |
| no trailing newline | correct, 8/8 |
| two trailing newlines | correct, 8/8 |
| CRLF line endings | correct, 8/8 |
| one leading blank line | correct, 8/8 |
| trailing spaces | correct, 8/8 |

Every asserted answer value is derived from the component rows, the dated correction and the
summary's unchanged record/decision while building from seed/; no reference answer value is
typed independently of the material.
