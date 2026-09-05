This candidate is a positive mechanical API migration. It makes completeness difficult by
requiring one exact keyword-only public signature and consistent updates across a large,
multi-package application tree: direct calls, defaults retaining the callable, dispatch
tables, aliases, registry reflection, comprehensions, lambdas, late imports, services,
adapters, integrations, and the supplied integration test. The plausible trap is changing
the visible definitions and direct calls while leaving a reflected `make_tag` string or an
indirect positional tone call; the old reflection can still appear to work through its
fallback, so that answer is confidently wrong.

The answer is positive: the migration must be completed successfully.

Reference: `ref/solve.py` is 47 lines, roughly 300 output tokens.

Selfcheck and checker runs:

- `selfcheck.py`: direct ok; default ok; batch ok; reflection ok; exit 0.
- `test.py` against the generated reference answer: `SCORE 14/14`, `PASS`,
  `VERDICT correct`, exit 0.
- A7 item 1, correct content with no trailing newline: pass — `SCORE 14/14`,
  `PASS`, `VERDICT correct`, exit 0.
- A7 item 2, correct content with two trailing newlines: pass — `SCORE 14/14`,
  `PASS`, `VERDICT correct`, exit 0.
- A7 item 3, correct content with CRLF endings: pass — `SCORE 14/14`,
  `PASS`, `VERDICT correct`, exit 0.
- A7 item 4, correct content with one leading blank line: pass — `SCORE 14/14`,
  `PASS`, `VERDICT correct`, exit 0.
- A7 item 5, correct content with trailing spaces on one line: pass — `SCORE 14/14`,
  `PASS`, `VERDICT correct`, exit 0.
- A7 item 6, definition-order violation (the prompt fixes order): fail —
  `SCORE 13/14`, `VERDICT confidently_wrong`, exit 1.
- Plausible wrong answer, reflected lookup left as `make_tag`: fail — `SCORE 13/14`,
  `VERDICT confidently_wrong`, exit 1.
- Untouched sandbox: fail — `SCORE 7/14`, `VERDICT visibly_failed`, exit 1, no traceback.

No checker defect was found in items 1–5, so none required fixing. One deliberate limitation is
that the hidden checker does not read or run the supplied test file, in accordance with the
contract's prohibition on trusting contestant-written tests; the application oracle checks
the migrated package independently. No other uncertainty is known.
