Candidate 3 is the knowing-when-to-stop variant. It makes the model apply two explicit boundaries precisely: a comment begins only at the specified ASCII-space boundary, and only the first three eligible runs are transformed. The tempting near-miss uses a conventional regex word boundary and transforms every apparent number, so it looks good on ordinary one-to-three-number inputs but changes comment text, fourth runs, and Unicode-edge cases.

Validation outcomes (all commands exited as noted):

- `python selfcheck.py`: examples 1–8 each `ok`; `selfcheck: PASS (8 examples)`; exit 0.
- Reference: `SCORE 24/24`; `PASS`; `VERDICT correct`; exit 0.
- Deliberately wrong near-miss: `SCORE 18/24`; `FAIL ['fourth preserved', 'unicode left is open', 'unicode right is open', 'comment after space', 'comment at start', 'hash after two spaces']`; `VERDICT confidently_wrong`; exit 1.
- Empty sandbox: `SCORE 0/24`; `FAIL ['load solution', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run']`; `VERDICT visibly_failed`; exit 1.

The reference is 36 lines and approximately 250 tokens. It uses only the standard language runtime and has no randomness, clock dependence, or external input. The checker has 24 fixed subchecks and an independent 45-second watchdog. No unresolved uncertainty.
