# Quarterly dwell audit

You are working in a checkout of the cordage-mesh repository; your current directory is the root of
that checkout.

Every stage the manifest names has a documented dwell. Some stages' documented dwell has been
proposed against, in the project's own branch workflow, since the last audit; produce this
quarter's audit of which stages' documented dwell is now **stale**, once you trace that history
forward by the rule currently in force.

A stage can carry more than one branch record. A record that was withdrawn before it merged
never took effect, at any date, and a later record can revert an earlier merge; find the rule
that says how to weigh these and apply it, not the plausible reading a single record suggests
on its own. A branch's own record only says whether it merged - it never says whether the
document was actually brought in line with it, so a document that still reads the same as
always is not, on its own, proof that nothing changed.

The project's own rules also decide which stages are actually included in this audit: some
stages fall outside its current scope even though their documented dwell disagrees with the
history. Find the rule that is currently in force and apply it, not a claim that predates it.

Write the audit to a new file `dwell-audit.txt` in the root of the workspace. It must contain exactly
these three lines, in this order:

    stale_dwell: <the stage names, alphabetical, separated by commas>
    net_dwell_change: <the sum, in seconds, by which those stages' documented dwell exceeds
their module's dwell constant, a plain integer>
    scope_note: <the identifier of the note that governs which stages are in scope>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the audit.

Work until the audit is complete, then stop.
