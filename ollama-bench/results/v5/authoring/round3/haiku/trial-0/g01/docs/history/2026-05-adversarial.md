# 2026-05 adversarial review

The release review added combinations rather than new semantics. Each source
alias was paired with its long name, each global key alias with a source-local
alias, and each accepted action with positive, negative, and zero deltas.
Administrative changes were placed before and between accepted duplicates.
Labels were repeated with case changes, edge spaces, empty strings, and tabs.

The review's purpose was to catch implementations that get every individual
rule right in isolation but apply rules in the wrong sequence. In particular:

* source creation precedes action rejection;
* action rejection precedes key and label canonicalization;
* source canonicalization precedes source-specific key lookup;
* key canonicalization precedes entry identity lookup;
* accepted contribution and occurrence update precede label merge;
* no update changes an existing position.

The benchmark's hidden cases follow these combinations. They do not introduce
malformed input or unstated policy. A solver should implement the release fold,
not guess behavior for values outside the documented valid schema.
