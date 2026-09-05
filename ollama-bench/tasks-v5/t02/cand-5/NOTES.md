This is the large-band t02 candidate. It keeps cand-2's yes/no comprehension shape and
two-line evidence artifact, but the target's meaning is distributed over a release-control
package, a frozen-snapshot call path, current policy records, and a longer archive of migration
and incident reviews. The trap is that a nearby all-required helper and current records make the
legacy-looking any-of aggregation appear plausible; a solver must trace which helper the public
function actually calls. The variant uses A4 levers 1 (more material held and reconciled), 2
(plausible wrong any-of answer), and 3 (normalization -> catalog -> identity/window -> chain ->
veto/conflict -> quota in series).

The correct answer is negative: the implementation does not exactly satisfy its docstring. The
decisive evidence is line 77 of seed/release_control/policy_chain.py, whose any-of aggregation
can grant when an applicable required constraint fails.

Reference solution: 2 nonblank lines, 2 physical lines, roughly 24 output tokens. It stays well
under 5,000 output tokens.

A7 checker probe outcomes (the prompt fixes ANSWER before EVIDENCE, so item 6 is an order
violation and must fail):

- reference: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 1 correct content, no trailing newline: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 2 correct content, two trailing newlines: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 3 correct content, CRLF line endings: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 4 correct content, one leading blank line: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 5 correct content, trailing spaces on one line: pass — SCORE 3/3, PASS, VERDICT correct, exit 0
- 6 order violation: fail — SCORE 0/3, FAIL, VERDICT visibly_failed, exit 1
- plausible-but-wrong positive: fail — SCORE 2/3, FAIL, VERDICT confidently_wrong, exit 1
- untouched sandbox: fail — SCORE 0/3, FAIL, VERDICT visibly_failed, exit 1

No checker defect was found in items 1-5; the parser intentionally strips only
unspecified surrounding whitespace and tolerates all listed line endings/newline counts. The
checker does not inspect contestant tests or count files. The only flagged doubt is that the
seed is synthetic release-control source and review material rather than a captured production
repository; its modules and records are internally cross-referenced and all are relevant to
the decision path, but this realism judgment remains the main uncertainty.
