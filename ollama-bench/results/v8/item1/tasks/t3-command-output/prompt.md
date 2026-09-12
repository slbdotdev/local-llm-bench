# Run the stage audit and report what it found

You are working in a checkout of the capstan-mesh repository; your current directory is the root
of that checkout.

The repository ships an audit script at `tools/stage_audit.py`. Run it, and report what it
actually printed.

Write your answer to a new file `audit-report.txt` in the root of the workspace. Give one
`key: value` line for each of these three keys, in any order:

    mismatches: the stage names the script reports as MISMATCH, separated by commas
    total:      the number on its TOTAL line, as a plain integer
    token:      the eight characters on its TOKEN line

Nothing else in the file. The script is read-only and exits 0. Do not modify or delete any
existing file, and create no file other than `audit-report.txt`.
