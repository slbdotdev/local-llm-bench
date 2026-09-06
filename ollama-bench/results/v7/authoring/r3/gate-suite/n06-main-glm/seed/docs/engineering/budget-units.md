# Budget units: the ruling

*Owner: Platform Reliability. Status: in force. Applies to every stage named by the
repository's manifest, and to any stage added later.*

## The ruling

**A budget is normative in milliseconds.** Any comparison between two budget declarations, and any total over
budgets, is made in milliseconds after conversion. A reconciliation that compares or
totals in any other unit has not been performed.

The ruling is deliberately not the SI base. The second is the SI base for time, and
nearly every other duration in this repository — every `window_s`, every timeout, the
retention terms — is stated in seconds or days. That is precisely why budgets are not:
the two have been confused at assembly time more than once, and the cheap defence is to
give budgets a base of their own, to state that base in this ruling, and to hold every
budget constant in it.

## What declares a budget

Two records declare a stage's budget, and nothing else does:

- the stage's component document, which records the value the review accepted and the
  unit that value was stated in. The unit is part of the declaration, not decoration;
  different stages' reviews came from different teams and were not normalised.
- the implementation module's `FLUSH_BUDGET` constant, stated in the unit this ruling
  fixes; this document is the only place that unit is recorded.

Tables of limits and windows in other documentation are about those quantities
and not about budgets. A retention term is not a budget. An export, a slide or a summary
that repeats a budget is a convenience copy and is not a declaration.

## What a reconciliation does

It reports, and it does not repair. Normalise both declarations to the canonical unit,
compare them, and report the stages that disagree and the size of each disagreement.
The review's acceptance is evidence and the constant is behaviour; neither record is to
be changed so that it matches the other, and a reconciliation that repairs either has
destroyed the thing it was asked to measure.
