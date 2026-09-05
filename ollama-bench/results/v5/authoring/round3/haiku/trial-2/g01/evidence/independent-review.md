# Independent release review

Two reviewers implemented the contract from different evidence subsets and
then compared their result trees on the complete fixture catalog. The first
read the current package and JSON configuration. The second read caller notes,
history, and regressions. Their agreement depended on resolving the old rules
as superseded rather than averaging conflicting behaviors.

Both reviewers listed the same current invariants: exact source aliases after
ASCII-space trimming; key edge-space trimming, casefold, global then local one-
step aliases; accepted add/remove/adjust/hold with multipliers one, minus one,
one, zero; rejected ignore/void; source lifecycle before policy; policy before
key and labels; first-seen source/key/label order; accepted-only occurrence and
label state; signed integer arithmetic; exact fresh public shape.

The review specifically compared cases where a plausible rule would agree on
the final total but differ elsewhere: sorted versus first-seen order, raw versus
weighted totals, all-action versus accepted counts, rejected label leakage,
zero dropping, broad whitespace, and source-local identity. These are the
reasons the task material spans multiple modules and a longer history.

No unresolved behavior was found for valid input. Malformed input, runtime
configuration changes, package import paths, and serialization errors remain
outside the contract. The benchmark implementation should inline the release
facts it needs rather than open these seed files during grading.
