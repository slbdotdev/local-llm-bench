This candidate combines the two migration traps rather than isolating them: the
public callable swaps its payload/kind positions and gains two keyword-only options.
Those options must propagate through the late import cycle, default sender, batch
comprehension, transport wrapper, formatter, reflection, and fallback. The output
still displays kind before payload, so symmetric or casually reordered calls can look
right until the asymmetric checks. A plausible near-miss keeps the old argument order
or drops `stamped` in one wrapper while remaining runnable and fluent.

Reference size: 60 lines across `ref/`, about 300 lexical/output tokens. Self-check:
reference -> to be recorded after running; near-miss -> to be recorded after running;
empty sandbox -> to be recorded after running. No known uncertainty at authoring time.
