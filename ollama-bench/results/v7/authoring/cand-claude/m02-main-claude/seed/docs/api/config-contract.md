# API contract - published configuration surface

*Config contract v3. Supersedes v2, which named stages by hand and went stale
within a quarter; this version states a rule instead.*

## The rule

A stage's configuration surface is **published** under this contract when its
effective SLA headroom - the `SLA_HEADROOM` constant in the stage's own module,
never the `sla_headroom` row in its component document - is at least **45**.

From the module, for every stage the manifest names. A stage's own document is
not evidence either way: two audits already trusted a document's table over its
module and both were wrong, because a document can lag a module for weeks after
a headroom figure changes and nobody notices until the next audit.

## Why this is not a document question

v2 of this contract named nine stages by hand. Four of the nine had already
drifted from their module constants by the time the next quarter's audit ran,
because nothing kept the hand-written list in sync with the code. This version
is the rule the list should have been computing all along.

## What publication does not by itself authorize

A stage meeting the rule above is published. Whether a *change* to a published
stage's configuration surface may proceed is a separate question, governed by
the security boundary, which may freeze a published stage against a class of
change regardless of this contract. Publication and freedom to change are
independent findings and neither implies the other.

## History

- v1 (withdrawn): proposed publishing every stage above the median headroom.
  Withdrawn because the median moves every time a stage is added.
- v2 (superseded): named nine stages directly. Superseded by this version once
  the drift above was found.
- v3 (**in force**): the rule stated above.
