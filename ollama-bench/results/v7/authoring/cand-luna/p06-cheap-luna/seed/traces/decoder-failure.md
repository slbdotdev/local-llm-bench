# Decoder failure trace

The relay smoke run captured a one-character overread at the handoff mark.  The trace points
to the window decoder used by the relay call record, not to the assertion in the visible
test.  The old branch labels the interval inclusive and adds one to the stop position;
that is the production defect.  The contract decision is the source to consult for the
repair, and the test file is evidence of the intended behavior.

Observed request: opening mark 2, handoff mark 5, returned span included position 5.
Observed consequence: the handoff byte was consumed twice by the downstream acknowledgement.
