# Escalation contact directory fix

You are working in a checkout of the solder-brook repository; your current directory is the root of
that checkout. This task concerns exactly two files: `data/owner-directory.csv` and `data/escalation-secondary.csv`. Do not modify or delete
any other existing file, and create no file other than the report below.

Each file records, one row per stage, where that stage's escalation contact is filed, and each
file applies its OWN rule for what the right directory is -- they are not the same rule, and
the two files are expected to disagree for some stages on purpose. A handful of rows in each
file violate that file's own rule and have done since a rename that was never fully swept
through. Work out, separately for each file, which of its own rows violate its own rule, and
correct only the `contact_path` field of those rows, in place. Do not change a row just
because the two files disagree on it -- some disagreement is correct. Everything else about
the two files -- their line endings, every other field, every byte of every owner name,
including the accented ones -- must come out of your edit exactly as it went in. Do not "fix"
an accented character and do not change a line ending anywhere in either file, including in
rows you do not otherwise touch.

The tree names more than one file that could plausibly be "the" cause. Only one of them is
actually misconfigured; find it by reading, not by guessing from where the symptom was first
reported.

When you are done, write env-report.txt to the root of the workspace. It must contain exactly these
three lines, in this order:

    corrected: <the stage names you fixed, alphabetical, separated by commas>
    root_cause: <the path to the configuration file responsible, written exactly as that file's
        own name for itself appears in the material that explains the bug -- copy it, do not
        normalise it>
    bytes_preserved: <a plain integer: the total number of characters, across the `owner`
        column of both files combined, whose Unicode code point is greater than 127 -- every
        accented or non-Latin character in every owner name in both files, counted once each>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Work until the report and both edits are complete, then stop.
