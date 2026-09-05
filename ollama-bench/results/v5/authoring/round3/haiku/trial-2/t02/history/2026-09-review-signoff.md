# 2026-09: review sign-off

Status: CURRENT.
Record identifier: rc-202609-signoff.

This final review closes the source reconciliation for the release-control
decision. The public function is not a policy editor. It consumes a normalized
request, one catalog revision, and one frozen snapshot. The source map,
current-contract record, and edge-case matrix are the controlling references
for this review.

## Required sequence

The reviewer must account for request normalization, published rule selection,
active membership and assurance, request-window validity, every applicable
required chain node, current deny overrides, audit conflicts, and committed
quota. Each stage feeds the next. A true intermediate check cannot authorize a
request that later fails.

## Sign-off invariants

1. Unknown capabilities fail closed.
2. A missing required node is not a pass.
3. An applicable false node has the documented effect even when another node
   passes.
4. Legacy aggregation belongs only to archived replay.
5. Historical grants are evidence, not current authorization.
6. Matching unexpired denies have documented veto precedence.
7. Conflicting current audit observations have documented veto precedence.
8. Quota is read after policy and veto checks.
9. Snapshot data is not rebuilt between checks.
10. The boolean result and review trace describe the same decision.

## Review method

Compare the public docstring with the actual call path. For each sentence,
locate the adapter that supplies its fact, then follow the returned value
through the selected catalog row and chain. Do not infer behavior from helper
names, archived examples, or a passing intermediate check. Record the exact
source line that most directly settles any mismatch.

This packet is a review record for maintainers and does not instruct the
reviewer to change the source under examination.

