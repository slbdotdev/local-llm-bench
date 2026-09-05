# 0031 — dispatch capacity raised

The dispatch stage was built with a limit of 48 entrys and a 90 second pending window. Both were
raised after the second quarter's backlog: the limit to twice its original value and the window
by half again, in the implementation and in the manifest together, on the reasoning that the
stage was refusing work it had the capacity to hold.

The change was made in `src/NorthstarLedger/dispatch_core.py` and in the `dispatch` section of
`config/manifest.json`, and those two are the authority on what the stage does today. The
narrative pages were not revisited at the time, which is the ordinary way a document and a
program come apart, and is why a maintainer note records what the stage is actually configured
with rather than what a page says it was configured with.

This entry records what was decided. It is history and is not rewritten when the numbers move
again.
