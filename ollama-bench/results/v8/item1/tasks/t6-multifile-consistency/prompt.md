# Raise one limit in all four places

You are working in a checkout of the futtock-mesh repository; your current directory is the root
of that checkout.

The `attestation` stage's handle limit is being raised from 96 to 160. The project records a
handle limit in four places and all four have to agree: the module constant, the manifest entry,
the configuration table in the stage's document, and the defaults assertion in the stage's test.
Find all four and change them. Change nothing else - no other stage's limit, and no other file.

The repository ships `tools/verify_attestation.py`, which prints one verdict line saying whether the
four agree. Run it **after** your change and quote the line it printed.

Then write a new file `consistency-report.json` in the root of the workspace, a single JSON object
with exactly these four keys:

    "paths"    a JSON array of the four paths you changed, as they appear in the repository
    "old"      the previous value, as a number
    "new"      the new value, as a number
    "verified" the verdict line `tools/verify_attestation.py` printed, exactly as it printed it

Do not create any file other than `consistency-report.json`.
