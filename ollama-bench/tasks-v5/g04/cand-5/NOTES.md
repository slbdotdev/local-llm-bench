This candidate makes a multi-stage ledger repair hard: the solver must reconcile eleven
complete region feeds with current policy, rates, aliases, and superseded history, then
filter, round per row, group, sort, and render in series. It uses A4 levers 1 (substantially
more required material), 2 (captured/void and historical rounding rules are plausible
traps), and 3 (serial eligibility, conversion, grouping, ordering, and formatting).

The plausible wrong answer is to resurrect the archived \`captured\`-row rule. It stays
well-formed and looks operationally reasonable, but produces the wrong close. The correct
answer is positive: the close has a non-empty accepted population and a positive total;
this is not a “nothing found” variant.

Reference solution: 67 lines, roughly 600 output tokens. \`selfcheck.py\` exited 0.
\`test.py\` against \`ref/\`: SCORE 10/10, PASS, VERDICT correct, exit 0.

A7 outcomes:

1. Correct content, no trailing newline — pass (\`correct\`).
2. Correct content, two trailing newlines — pass (\`correct\`).
3. Correct content, CRLF line endings — pass (\`correct\`).
4. Correct content, one leading blank line — pass (\`correct\`).
5. Correct content, trailing spaces on one line — pass (\`correct\`).
6. Correct content, reordered helper definitions — pass (\`correct\`).
7. Plausible wrong answer using the archived captured-row rule — pass (\`confidently_wrong\`).
8. Untouched sandbox with the target absent — pass (\`visibly_failed\`).

Checker defect found and fixed: none. The checker intentionally ignores trailing whitespace,
blank-line count, and line-ending style; all A7 probes passed on the first run.

Uncertainty: none known. The fixed-input digest covers every named seed input while allowing
unrelated extra sandbox files.
