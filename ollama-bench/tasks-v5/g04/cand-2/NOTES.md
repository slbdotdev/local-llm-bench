This candidate makes semantic repair hard: the visible findings are AST-level, but the
mutable-default fix must preserve both explicit route tables and isolation of implicit ones.
The tempting wrong answer is to change only the warning syntax or to retain a shared default
map, which looks conventional and passes simple lookup examples.

Reference size: 22 lines, roughly 80 output tokens. Self-verification: reference -> correct
(SCORE 9/9, PASS); near-miss -> confidently_wrong (SCORE 8/9); empty sandbox -> visibly_failed
(SCORE 8/9). No known uncertainty.
