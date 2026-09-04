This candidate makes semantic repair hard after a compact lint pass: the resolver must retain
first-match order, distinguish wildcard and mismatched actions, treat any false-y predicate
result as a non-match, skip malformed rules, and preserve explicit false-y effects. The
tempting wrong answer is `rule.get("effect") or "deny"`, which is clean and conventional but
erases the difference between an absent effect and an explicit empty, zero, or None effect.

Reference size: 19 lines, roughly 75 output tokens. Self-verification: pending execution.
No known uncertainty.
