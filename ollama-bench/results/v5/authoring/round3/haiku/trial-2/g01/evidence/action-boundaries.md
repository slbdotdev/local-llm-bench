# Action boundary cases

The release action table is closed. Accepted actions are add, remove, adjust,
and hold. Rejected actions are ignore and void. The valid input schema permits
those documented action strings; the adapter does not need a fallback for an
unknown action, but the two rejected strings must be handled distinctly from a
zero result.

An add has multiplier one and an adjust has multiplier one. A remove has
multiplier minus one. A hold has multiplier zero but is accepted. All accepted
changes count once, even with delta zero, even when their contribution cancels
the running total, and even when their labels become empty after normalization.

Ignore and void contribute nothing: they do not create an entry, update an
entry, increment an occurrence, or merge labels. They are still processed after
the source bucket is created. This difference makes a rejected-only source
visible as an empty bucket.

The policy gate precedes canonical key and label processing. This matters if a
rejected change uses a key alias or a label that would otherwise be new. The
administrative data is not allowed to seed future visible state. The source
canonicalization is the one exception because it controls bucket lifecycle.

The output total is an integer sum of each accepted delta times its action
multiplier. No rounding, clamping, absolute value, or conversion is permitted.
The output occurrence count is the number of accepted changes for that key,
not the number of nonzero contributions.
