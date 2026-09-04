This candidate makes stopping discipline hard: the checker requests narrowly scoped API/style
metadata, while a formatter or CSV rewrite can easily exceed the change bound or lose quoting.
The tempting wrong answer is manual comma joining or treating a skipped `None` row as an empty
CSV row; both look reasonable until quoted and sparse inputs are checked.

Reference size: 15 lines, roughly 60 output tokens. Self-verification: reference -> correct
(SCORE 8/8, PASS); near-miss -> confidently_wrong (SCORE 7/8); empty sandbox -> visibly_failed
(SCORE 7/8). No known uncertainty.
