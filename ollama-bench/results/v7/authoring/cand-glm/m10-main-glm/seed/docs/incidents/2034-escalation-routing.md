# Incident: escalation contacts pointing at the wrong directory

*Filed 2034-04-02. Status: root cause found, fix pending -- the two contact files were never
swept after the rule below changed.*

## What was reported

Pages for several stages were landing in the wrong on-call channel. The report was filed
against `tests/test_retention.py`, on the theory that the test's fixtures were stale. They are not:
the test passes and always did. The channel routing does not come from a test at all.

## The two rules -- they are not the same rule

`data/owner-directory.csv` (the primary contact) puts a stage on the escalation root only when
BOTH hold: its own history status is `accepted`, and its own module opts in with
`ESCALATION_ELIGIBLE = True`. `data/escalation-secondary.csv` (the backup contact) is
deliberately looser: `accepted` alone is enough, because a backup contact does not require the
same opt-in as the primary one. **The two files therefore legitimately disagree for any stage
that is accepted but has not opted in**: the primary file correctly shows the owners root and
the secondary file correctly shows the escalation root for that stage, and neither row is
wrong. A line-by-line diff of the two files will surface those rows as differences right
alongside the genuinely wrong ones, with no way to tell which is which from the diff alone --
that has already misled one reviewer of this incident and is not a shortcut past applying each
file's own rule.

Status is recorded nowhere but a stage's own history entry; eligibility is recorded nowhere but
that same stage's own module. Neither the manifest nor a component document repeats either
fact.

## The actual root cause

`config\routing.json` names both roots for a Windows-hosted deployer, using its own separator:

    "owners_root": "notify\\owners"
    "escalation_root": "notify\\escalation"

Both data files use the forward-slash form of the same two roots, which is correct for them --
the loader that reads them runs cross-platform and always has. The two roots were renamed in
`config\routing.json` on 2034-03-01 without a matching sweep of either contact file, so a handful of rows in
each file still point at whichever root used to be correct for that stage before the rename.
Comparing a file's paths against `config\routing.json`'s raw value character for character, without converting
the separator first, makes every row in that file look wrong; that is not a finding, it is the
comparison being done incorrectly.

## Disposition

Fix the rows that violate their OWN file's rule above, in both contact files, so each stage's
`contact_path` matches what that file's rule calls for. Leave every row where the two files
disagree on purpose exactly as it is. Do not touch `config\routing.json` and do not touch the test that was
originally blamed.
