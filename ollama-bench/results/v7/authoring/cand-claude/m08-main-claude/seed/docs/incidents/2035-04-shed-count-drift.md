# Incident note — 2035-04 — shed-count drift

- Opened: 2035-04-06
- Status: **open, no root cause** (rotation changed before the trace was run)
- Reported by: on-call, Platform Reliability

## What was observed

Three separate shed-count spikes this quarter were originally reported as a capacity
problem and escalated as one. It is not: capacity was never close to any documented
limit at the time of any of the three spikes, and every manifest section involved
matched its module exactly.

## What was confirmed before the rotation changed

Every stage's component document carries a `capacity_ack` code in its configuration
table — the review cycle the document was last checked against — and every stage's
module carries the code it was actually rebuilt under, as
`DEFAULT_<STAGE>_CAPACITY_ACK`. For eighteen of the nineteen stages this quarter, the
two agree, which is expected and is not a finding. For exactly one stage, they do
not: the module was rebuilt under a later review cycle than its own document
reflects, and the shed-count spikes on-call chased tracked the module's cycle, never
the document's. That stage's module is the primary suspect, and the drift itself —
not a request rate, not a deploy schedule, not the manifest — is the defect this note
narrows to.

## What was not established

Nobody on the rotation determined *why* the document and the module disagree: whether
the document was never updated after a deploy, whether the module was hot-patched
without a doc change, or whether the mismatch predates both of the engineers who
looked at it. A firmware-level trace was requested and never run. This note is closed
as inconclusive rather than reassigned, because nobody currently on the rotation has
the context to pick it back up cheaply, and the drift itself is small enough that it
is tracked as debt rather than escalated further.

## Handoff

Whoever picks this up next should start from the module identified above, not from
this note's own guesses about cause. The consequence and the compatibility guarantee
of eventually fixing it are tracked separately, in the usual places, keyed by that
stage's name.
