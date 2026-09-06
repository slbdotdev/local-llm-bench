# Maintenance guidance

The translation layer is being retired in pieces.  A source routine is considered
repaired only when its locked check can read the exact expected source and exercise both its
translated input and its pass-through behavior.  The checks are evidence, not instructions to
edit themselves.  The roster is complete; no unlisted source module is part of this change.

Preserve the encoding and newline style already used by the project.  A summary is required so
the release desk can reconcile the number of repaired routines with the roster.  A test
that is changed to silence a failure is a release-blocking scope violation.
