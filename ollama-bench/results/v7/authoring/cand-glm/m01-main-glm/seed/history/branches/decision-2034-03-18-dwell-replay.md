# Decision: how a stage's dwell replays

- Date: 2034-03-18
- Status: **in force**

## The rule

A stage's current dwell is the proposed number of its most recently merged branch
that has not since been reverted by a later merge. Read every branch record filed
for the stage before deciding this, not only the first: a stage's dwell can be
raised by one branch and then restored by a second, later one, and the first
record alone does not say so.

A branch that is withdrawn before merging never took effect, at any date; its
proposed number is not a claim about the stage's dwell, only a proposal that was
not accepted. A branch that reverts an earlier one restores the stage's dwell to
the module default and proposes no number of its own.

A stage with no branch record at all has never had its dwell proposed against; its
dwell is whatever its component document has always said.

## Why a reverted branch carries no number of its own

A branch that reverts an earlier one is not a second opinion about what the dwell
should be; it is the withdrawal of the first opinion. Giving it a number of its own
would let a revert be replayed twice with two different results depending on which
field a reader trusted, which is exactly the ambiguity this note exists to close.

## Why a withdrawn branch is not evidence of anything

A withdrawn branch was considered and not accepted. It is kept in this directory as
a record that the option was raised, in the same spirit as a withdrawn history
entry elsewhere in this project - never as a live instruction, and never as a number
a later reader should apply.

## Why a merged branch is not the whole answer either

A branch's own record says a proposal was accepted. It does not say whether the
document was ever updated to match - that is a fact about the document, not about
the branch, and this note does not assume one from the other. A stage's document can
lag an accepted merge indefinitely; nothing here reaps that automatically.

## History

An earlier draft of this note said a stage's dwell was simply its most recent branch
record, merged or not. It was corrected within the week once a withdrawn proposal on
a since-decommissioned stage was replayed as though it had merged.

## Scope

This note governs how to replay a stage's branch history into a current dwell. It
does not decide which stages are actually included in a dwell audit; that is
governed by the current release note under `docs/release-notes/`, not by this
note.
