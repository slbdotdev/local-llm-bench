verdict: PASS

fair: yes — prompt, incident note (`seed/docs/incidents/2034-escalation-routing.md`) and grader agree on every rule; I solved it blind from the prompt and matched `ref/` exactly.

solved_it: yes — my independent answer (13 stages; `config\routing.json` raw with backslash, confirmed in the note's bytes at lines 32/39/41/49; 35 non-ASCII owner characters, recounted from the seed CSVs myself) matched `ref/env-report.txt` and the selfcheck reference byte-for-byte. I nearly went wrong on the accepted-but-not-opted-in rows (ledger, lineage, throttle, backfill primary-side) until I applied "BOTH hold" per file instead of diffing.

checker: sound — all seven run clean: selfcheck 16/16 cases land as NOTES §9–10 declares (reference 8/8 correct, empty 1/8 visibly_failed no traceback, seven wrong-course cases confidently_wrong, two unsafe cases, five deliverable-only perturbations all 8/8); probe_candidate's four "GRADER DEFECT" lines are the documented §10 exception — verified in `probe_candidate.py` `deliverables()` (diffs ref vs seed) that those perturbations rewrite the two byte-exact CSVs, not just the report, and the prompt states that byte requirement plainly; probe_idempotence ok; check_rung0 clear; check_index_leak clean (ESCALATION_ELIGIBLE only in each stage's own module); check_load_bearing 31/6/12360/29178/42.4%; check_tools clear.

shortcut: 41 files — 3 read whole (both CSVs + incident note) plus two greps consulting 38 files' single decisive lines; no sub-5 path exists: the manifest carries only name/module/class/limit/window/owner (no status, no eligibility), a two-file diff misses all 9 both-category rows and wrongly includes 4 legitimate-divergence rows, and `config/manifest.json`'s already-duplicated limit/window fields determine nothing.

harvest: 19/19 units by `grep -rn "Status: **" history/` — one grep puts every stage's decisive status on screen (filename-prefixed), fully determining the secondary file; `grep -rn "ESCALATION_ELIGIBLE" src/solder/` does the same for the primary file but its constant name is not prompt-visible (one module must be opened first). Decisive lines sit at fixed offsets (status line 4, flag line 14) but frames are NOT byte-identical (8 frame-classes over 19 files after normalization), so tail-style attacks are imperfect. The answer still cannot be finished from greps alone: both rules, the root cause and its exact form live in the incident note, and the count lives in the CSVs — no single grep computes the two-rule join.

tools: clear — check_tools verbose: 19 modules run rc=0, 0 bytes stdout, 0 scored units.

notes_claims: verified — files map sums 29175 vs 29178 total (rounding, as §3 states); seed_files 86; 31 load-bearing paths (2 named_in_prompt + 5 + 13 corrected stages × status/eligibility); 42.4% = 12360/29178; 56.5% = 16475/29178; ref report values 13/`config\routing.json`/35; §2's five failure courses each have a selfcheck case; §10's perturbation adjudication confirmed in checker source; README.md:52 points to `docs/incidents/` so the note is discoverable without luck.

tiers: Haiku fails at the two-rule join — holding status∧ESCALATION_ELIGIBLE per stage while applying a different rule per file, then reproducing CRLF/precomposed-UTF-8 bytes in place — while a careful Sonnet is signposted past every trap (the prompt says "copy it, do not normalise it" for the backslash root_cause; the note names the diff trap and the separator trap explicitly).

workhorse_failure: real — the byte-exact hashes on both corrected CSVs (`test.py` CONFIG.editable) genuinely measure mode 10: preserve line endings and accents while editing exactly the violating contact_path fields.

hard_to_do: no — a bounded 19-stage sweep with both rules stated verbatim in the incident note; the revision (three bug categories + legitimate divergence breaking the diff coincidence) makes the task harder to do, not harder to understand, and is stated plainly, not obfuscated.

fix: none required. One minor observation, not verdict-changing: NOTES §6 / test.py LOAD_BEARING declares 31 paths by listing only the 13 corrected stages' status/eligibility pairs; the honest full-verification path needs all 19 pairs (41 files), so the declared 42.4% floor slightly understates material necessity. Raising it only raises coverage; the gate passes either way.

final verdict: PASS
