Candidate purpose: a positive comprehension variant over a coherent authentication service.
It requires tracing the production route through canonical identity derivation, the lockout
ledger, credential verification order, policy duration, and response construction. The tree
also contains multiple adapters, tests, configuration tables, and five archived releases.

Trap: a session path, an old release, and a 60-second policy value each look like evidence;
none is the current production behavior by itself. The tempting wrong answer cites a decoy
mechanism instead of following all five dependent steps.

A4 levers used: (1) substantially more material that must be held and reconciled, (2) a
plausible-looking but wrong decoy, and (3) serial identity -> gate -> verify -> record/clear
-> route reasoning. The correct answer is positive.

Reference: 3 logical output lines, roughly 43 output tokens. The cited span is the complete
`process_login` body in the current request-path module; supporting identity, policy, ledger,
audit, and response behavior is named in the explanation.

    A7 checker probes (the first five must pass because line endings and surrounding whitespace
    are not specified; field order is specified and its violation must fail):

    1. correct content, no trailing newline: PASS, exit 0, VERDICT correct
    2. correct content, two trailing newlines: PASS, exit 0, VERDICT correct
    3. correct content, CRLF line endings: PASS, exit 0, VERDICT correct
    4. correct content, one leading blank line: PASS, exit 0, VERDICT correct
    5. correct content, trailing spaces on one line: PASS, exit 0, VERDICT correct
    6. reordered fields: FAIL, exit 1, VERDICT visibly_failed (specified order violation)
    7. plausible decoy citation: FAIL, exit 1, VERDICT confidently_wrong
    8. untouched sandbox: FAIL, exit 1, VERDICT visibly_failed, no traceback

    Selfcheck: reference -> correct. The checker is deliberately self-contained and reads only
    answer.txt; it does not inspect contestant files or imports.

    Authoring correction: the first checker draft expected line 7 as the start of the cited
    span, while the generated function actually starts at line 6. The oracle was corrected to
    6-20 before the A7 probes; none of A7 items 1-5 exposed a formatting defect.

    Uncertainty: the source material is synthetic but internally coherent; the archived release
files are included as migration history rather than executable imports. No known checker or
prompt ambiguity remains.
