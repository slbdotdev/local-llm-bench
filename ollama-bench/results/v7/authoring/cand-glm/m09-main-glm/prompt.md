# Audit the duplicate quarantine lift

You are working in a checkout of the cinder-crest repository; your current
directory is the root of that checkout.

The quarantine timeline of the replay stage can be printed with:

    python tools/timeline_dump.py

(it reads the export at `data/quarantine-timeline.csv`). The project's
operations documentation states which timeline entries count as lifts and
which lift governs when a batch carries more than one; apply that documented
rule, not the entry shapes alone.

Exactly one batch in the timeline carries a duplicate lift. Find that batch,
work out its governing lift, and write the answer to a new file `lift-audit.txt`
in the root of the workspace. The file must contain exactly two lines, in this
order:

    batch: <the batch id exactly as the timeline prints it>
    governing_lift: <the governing lift's date, YYYY-MM-DD>

No header, no quotes, no explanation. It may end with a newline or not.

Do not modify or delete any existing file. Work until the file is complete,
then stop.
