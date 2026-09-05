# Release 3.2 contract fragments

This document is the release checklist used when the separated modules are
reviewed. It is intentionally a cross-reference rather than a replacement for
the source. “Current” means the 3.2 rules in the package and configuration; a
3.0 statement in the history is informative only.

## Input

The adapter receives a list of records. Each record has a string `source` and a
list `changes`. Each change has a string `key`, an integer `delta`, a string
`action`, and a list `labels` of strings. Empty strings and empty lists are
valid. The benchmark supplies this schema, so validation and error handling are
not part of the task.

## Bucket lifecycle

Canonicalize the record source as the record is visited. Create its output
bucket immediately, even when `changes` is empty or every change is rejected.
Buckets are ordered by the first record that names their canonical source.
Repeated source spellings merge into the existing bucket and never move it.

## Accepted changes

Action policy decides whether a change is accepted and supplies its multiplier.
The current policy has four accepted actions: `add` has multiplier 1,
`remove` has multiplier -1, `adjust` has multiplier 1, and `hold` has
multiplier 0. `ignore` and `void` are rejected. Rejected changes have no
effect at all except for the already-created bucket. Do not infer policy from
the sign of `delta`; a negative delta is valid for every accepted action.

For an accepted change, the contribution is `delta * multiplier`. An entry's
`occurrences` counts accepted changes, including `hold` and changes whose
contribution is zero. It does not count rejected changes.

## Canonical fields

Source aliases are exact after removing ASCII spaces at the two ends. Key
canonicalization removes ASCII spaces at the two ends, then applies
`casefold()`, then applies the global key alias table. Source-specific aliases
are applied after the global table. Do not use `strip()` for the outer source or
key operation: a tab is a real character in this format. Alias lookup is exact
after these stated steps; an unknown name remains its canonicalized spelling.

Labels are processed only for accepted changes. Remove ASCII spaces at both
ends, case-fold, and discard the result if it is empty. In each output entry,
retain the first occurrence of each canonical label and ignore later repeats.
Labels are ordered by their first appearance across accepted changes for that
entry. A label's original case is not retained: the canonical case-folded value
is emitted. Labels from a rejected change are never carried over.

## Output

Return a fresh list. Each bucket is a fresh dictionary with exactly `source` and
`entries`. Each entry is a fresh dictionary with exactly `key`, `total`,
`occurrences`, and `labels`, in that conceptual order. Entries are ordered by
the first accepted change for their canonical source/key. Existing entries are
updated in place conceptually, so a later duplicate does not move an entry.
The output must contain no other fields and the input must compare equal to its
pre-call deep copy after the function returns.

The output is JSON-like but the checker compares Python values. Integer arithmetic
must remain integer arithmetic, including very large values. No sorting,
deduplication by value, or truthiness shortcut is allowed for empty names,
empty lists, zero deltas, or zero multipliers.
