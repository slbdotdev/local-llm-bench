# v4 authoring process (overseer checklist), 2026-09-03

1. Author writes the task (prompt.md, seed/, ref/, test.py) per brief.md rules 1-5; `python selftest2.py tasks-v4 <task>`
   must print ref PASS and seed FAIL; an empty sandbox must print exactly `SCORE 0/TOTAL`.
2. Overseer audit: oracle independence (diff the oracle in test.py against ref/ after un-renaming symbols; > 40%
   verbatim overlap is a finding; a generator script that derives the oracle from ref/ is a reject), fairness
   (every hidden case derivable from the spec), termination, SCORE granularity (a valid-input-only solution
   should land near 0.5-0.7).
3. HAIKU GATE (brief section 7): 3 Haiku takers, same brief and graders. 3/3 pass or mean SCORE > 0.95 => too easy,
   revise, no cloud run. Otherwise proceed.
4. fp8 smoke on OpenRouter (agent dir results/pi-agent-v4: ZDR, price sort, Parasail pin), medium thinking,
   1800 s timeout for parity with the local ranking, one trial first, a second only if the first SCORE is in
   (0, 0.95); keep filter = brief rule 6 on the mean. Running USD ledger from the key API after every task;
   stop at the cap the owner set.
5. Keepers stay in tasks-v4/, rejects move to tasks-v4-rejected/ with the reason in report.md; report.md carries
   Haiku k/3 + mean and fp8 trials + mean per task.
6. Never edit a task while a ranking run that uses it is in progress (check results/*.pid and the ranking log).
