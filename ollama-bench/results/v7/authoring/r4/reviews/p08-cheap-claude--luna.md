verdict: REVISE
fair: yes — The prompt unambiguously defines the three outputs, and the reference agrees with the policy, histories, and derived holdings.
checker: sound — I ran the reference, dashboard, withdrawn-filing, superseded-entry, incomplete-key, key-order, and whitespace cases via selfcheck.py; all matched expected verdicts.
harvest: 0/6 by `records` — the best single giveaway grep showed raw filing rows and dashboard/policy material but no derived closing hold, so the answer cannot be finished without opening per-unit files.
declaration: honest
shortcut: 9 files, score 7/7 — The manifest, policy, accepted history entry, and six evidence files suffice; no shorter shortcut I found reaches full score.
notes_claims: the claim that no closing-hold value occurs anywhere under seed/ fails: `118` appears in history/0210-close-out.md as part of `QC-1187`.
tiers: Haiku fails at replaying all six holdings files and excluding withdrawals — a careful Sonnet-class model should pass because the policy states the rule and the records make each replay explicit.
hard_to_do: yes — The anti-harvest mechanism makes the solver read and reconcile six short records, not decipher hidden facts; this is harder to do but remains easy to understand.
fix: Change the final NOTES.md claim to say that none of the six closing holds occurs as a standalone numeric value in the material.
