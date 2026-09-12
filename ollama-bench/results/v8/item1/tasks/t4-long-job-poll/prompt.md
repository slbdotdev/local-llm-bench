# Start the stage scan, wait for it, report the result

You are working in a checkout of the dogvane-mesh repository; your current directory is the root
of that checkout.

The repository ships a scan at `tools/slow_scan.py`. It takes about nine seconds to run, which is
longer than a foreground tool call is allowed to take, so start it as a background job and poll it
until it has finished. The line you want is the one beginning `RESULT`; it is the last line it
prints. A `PARTIAL` line appears part way through and is not the result.

Write your answer to a new file `scan-result.json` in the root of the workspace, a single JSON
object with exactly these two keys:

    "token" the eight characters on the RESULT line
    "count" the number on the RESULT line, as a number

Do not modify or delete any existing file, and create no file other than `scan-result.json`.
