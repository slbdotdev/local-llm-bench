verdict: PASS
fair: yes — The prompt is unambiguous, and the unit-normalization challenge is difficult to do without making it difficult to understand.
checker: sound — selfcheck.py passed the reference, near-miss, unsafe, and whitespace-perturbation cases with their documented scores and verdicts.
shortcut: 42 files, score 7/7 — The shortest seed-only route used the manifest and ruling plus all 20 stage documents and all 20 implementation modules; no index, single docs page, or seed helper yielded the full answer.
notes_claims: verified
tiers: Haiku fails at per-stage unit normalization and aggregation — it is likely to add printed values or use seconds, while a careful Sonnet can apply the ruling across all stages.
fix: none
