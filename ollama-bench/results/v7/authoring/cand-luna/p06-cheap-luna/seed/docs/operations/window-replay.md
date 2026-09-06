# Replaying a relay window

For each named component, read its opening and handoff marks in the order recorded.  Replay
uses the interval beginning at the first mark and stopping before the second mark.  The
interval itself is derived from the two marks; no record is allowed to state a ready-made
span.  This page connects the call record to the per-component traces and is also the check
against accidentally repairing the assertion instead of the decoder.

If a component has no ordered pair, treat the material as incomplete rather than inventing a
boundary.  The supplied records each contain one bounded pair.
