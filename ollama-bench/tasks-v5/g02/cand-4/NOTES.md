This candidate stresses precise token-boundary reasoning in a source-to-source transformation. The repair must identify the maximal dotted expression at a real call site, so a tempting suffix/prefix search can rewrite an attribute subexpression or a merely similar name. It also must distinguish a call from attribute access and a newline-terminated expression while preserving layout.

Reference: ref/calls.py is 106 lines (roughly 700 output tokens), well under the 5,000-token limit.

Checker verification: reference -> SCORE 13/13, PASS, VERDICT correct; deliberately prefix-matching near-miss -> SCORE 12/13, VERDICT confidently_wrong; empty sandbox -> SCORE 0/13, VERDICT visibly_failed. The seed test suite has exactly one failing test before repair.

No known uncertainty.
