# Candidate 4 notes

This candidate stresses a small lexical state machine: quote state is toggled
only by quotes preceded by an even backslash run, comments begin only outside
quotes at the exact ASCII-space boundary, and the two-wrap limit resets for
each LF-separated record. The traps interact: a regex that ignores quoting
will wrap digits in quoted text and comments, while a global counter or a
conventional escaping rule mishandles other plausible cases. All characters,
including delimiters, CR, and line structure, must remain intact.

Validation results:

- `python3 selfcheck.py`: examples 01 through 11 each printed `ok`; final
  line was `all examples passed`; exit 0.
- checker with `ref/solution.py`: `SCORE 24/24`, `PASS`,
  `VERDICT correct`; exit 0.
- deliberately wrong regex near-miss: `SCORE 14/24`,
  `FAIL ['quoted digits', 'odd escaped quote', 'even escaped quote',
  'hash inside quote', 'hash at record start', 'hash after ASCII space',
  'limit resets per LF', 'unterminated quote', 'adjacent empty quote',
  'tab comment boundary']`, `VERDICT confidently_wrong`; exit 1.
- empty sandbox: `SCORE 0/24`, `FAIL ['load solution', 'not run', ...]`,
  `VERDICT visibly_failed`; exit 1.

The reference is 54 lines, 199 whitespace-delimited words, and 1,550 bytes,
roughly 300 output tokens. No known uncertainty.
