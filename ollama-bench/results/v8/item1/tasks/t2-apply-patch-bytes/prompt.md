# One constant, and not one byte more

You are working in a checkout of the bollard-mesh repository; your current directory is the root
of that checkout.

Raise the `ingest` stage's default handle limit from 120 to 184. The constant is `DEFAULT_INGEST_LIMIT` and
it is in `src/bollard/ingest_core.py`.

Use the `apply_patch` tool to make the change. Every other byte of that file must be identical
afterwards - every other line, its exact spacing, and every non-ASCII character in it. A
reviewer will compare the file byte for byte, so a reformatted, re-indented or re-encoded file
fails even if the constant is right.

Then write a new file `patch-report.json` in the root of the workspace, a single JSON object
with exactly these four keys:

    "file"     the path you changed, as written above
    "constant" the name of the constant you changed
    "old"      its value before, as a number
    "new"      its value after, as a number

Do not modify or delete any file other than `src/bollard/ingest_core.py`, and create no file other than
`patch-report.json`.
