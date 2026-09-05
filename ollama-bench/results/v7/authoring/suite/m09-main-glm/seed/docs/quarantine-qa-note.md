# QA note - spring audit follow-up

*Unsigned note found on the recovery desk, circulated during the spring audit.
Kept here because it is cited by two audit tickets. Nothing on this page has
been verified by Capacity Planning.*

## The flag

During the spring audit we flagged **batch CC-1087** as carrying a duplicate
lift: it shows a `quarantined` entry on 2034-02-14 and then two later entries
(2034-02-27 and 2034-03-01) that both look like lifts, so the second of the two
should be treated as void and the batch counted as lifted on the later of the
two dates.

Recommendation: replay reads CC-1087's effective lift as the later entry, and
the audit counts the batch against the duplicate-lift tally.

## What this page is not

This page is a desk note, not a policy reading. It was written from a screenshot
of the timeline printer, not from the export, and nobody has checked it against
the quarantine policy. If an audit ever turns on which batch actually carries a
duplicate lift, read the timeline and the policy for yourself and ignore this
note.
