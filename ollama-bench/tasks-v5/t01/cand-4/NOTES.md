This candidate makes semantic classification and exact reporting harder without adding much
writing: seven references span nested paths, a table, inline code, and a fenced code block. The
same current runbook contains both a live instruction and a historical quotation, so classifying
by filename or by a global replacement sweep gives a plausible but wrong result. Near-matches in
Markdown and an exact path in a non-Markdown file test the stated search boundaries.

Reference solution: 14 lines, roughly 220 output tokens (including the short Python writer).

Self-verification:

- format examples: PASS
- reference -> correct: PASS (`SCORE 14/14`, `PASS`, `VERDICT correct`)
- near-miss -> confidently_wrong: PASS (`VERDICT confidently_wrong`)
- empty sandbox -> visibly_failed: PASS (`VERDICT visibly_failed`)

Uncertainty: none known; the checker requires sorted coordinates and treats a complete valid but
incorrect classification as confidently wrong, while absent, malformed, or incomplete output is
visibly failed.
