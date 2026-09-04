This candidate combines the two migration traps rather than isolating them: the
public callable swaps its payload/kind positions and gains two keyword-only options.
Those options must propagate through the late import cycle, default sender, batch
comprehension, transport wrapper, formatter, reflection, and fallback. The output
still displays kind before payload, so symmetric or casually reordered calls can look
right until the asymmetric checks. A plausible near-miss keeps the old argument order
or drops `stamped` in one wrapper while remaining runnable and fluent.

Reference size: 61 lines across `ref/`, about 300 lexical/output tokens. Self-check:
reference -> exit 0, all seven checks `ok`. `test.py` against `ref/` -> `SCORE 15/15`,
`PASS`, `VERDICT correct`, exit 0. Near-miss with only the reflective lookup left
as `emit_event` -> `SCORE 14/15`, `VERDICT confidently_wrong`, exit 1. Empty
sandbox -> `SCORE 0/15`, `VERDICT visibly_failed`, exit 1. No known uncertainty.
