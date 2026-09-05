This candidate makes reconciliation hard by requiring a recursive audit across 26 substantive
module, operations, current-guidance, history, and archive documents. The trap is that the old
path appears in live instructions and in immutable historical evidence; updating every hit is a
plausible but wrong answer. It uses A4 levers 1 (more material held at once), 2 (tempting
over-update), and 3 (many ordered records whose coordinates and classifications must all agree).

The correct answer is positive: 37 live occurrences require UPDATE, while 18 historical or
archival occurrences require LEAVE, including six dated quotations embedded in current modules.

Reference solution: 61 physical lines, roughly 1,350 output tokens (55 records plus a short
Python writer).

A7 checker probes (all run against a correct 55-record answer):
- correct content, no trailing newline: PASS (SCORE 55/55, PASS, VERDICT correct)
- correct content, two trailing newlines: PASS (SCORE 55/55, PASS, VERDICT correct)
- correct content, CRLF line endings: PASS (SCORE 55/55, PASS, VERDICT correct)
- correct content, one leading blank line: PASS (SCORE 55/55, PASS, VERDICT correct)
- correct content, trailing spaces on one line: PASS (SCORE 55/55, PASS, VERDICT correct)
- ordering violation (prompt fixes order): PASS as a required failure (VERDICT confidently_wrong)
- plausible-but-wrong all-UPDATE answer: PASS (VERDICT confidently_wrong)
- untouched sandbox: PASS (VERDICT visibly_failed, no traceback)

Checker defect found and fixed: the filename validator initially tested the wrong quoted
backslash literal; it now rejects actual backslashes while accepting POSIX paths. A separate
authoring measurement check initially treated punctuation after the path as a suffix; I corrected
that coordinate check to treat punctuation as a boundary while excluding path continuations and
filename extensions. The checker accepts all A7 variations 1-5 without relying on newline style,
blank-line placement, or trailing spaces.

Uncertainty: the only judgment-sensitive case is the catalog sentence in seed/README.md; it is
explicitly a current catalog pointer and therefore UPDATE under the prompt's current-pointer
rule. No other known uncertainty.
