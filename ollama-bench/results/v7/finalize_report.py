#!/usr/bin/env python3
"""Fill the calibration report's after-tuning section from the artifacts, and nothing by hand.

    python3 results/v7/finalize_report.py

Inserts (or replaces) a `## 4. After tuning …` section immediately before `## 5.`, containing the
second-pass tables on the workhorse and the two neighbours' tables, and rewrites the "after
tuning" row of the headline table in section 2. Re-runnable: it replaces its own output rather
than appending a second copy, so a re-run after a late trial lands is safe.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summarize_cal as sc  # noqa: E402

REPORT = os.path.join(HERE, "calibration-2026-09-06.md")
BEGIN = "<!-- BEGIN GENERATED SECTION 4 -->"
END = "<!-- END GENERATED SECTION 4 -->"


def render(prefixes, heading):
    buf = io.StringIO()
    old, sys.stdout = sys.stdout, buf
    try:
        sys.argv = ["summarize_cal"] + list(prefixes)
        sc.main()
    finally:
        sys.stdout = old
    return "\n" + heading + "\n" + buf.getvalue()


def headline(prefixes):
    man = sc.manifests()
    tot = dict.fromkeys(sc.VERDICTS, 0)
    n = 0
    for (quant, band, tag, model), runs in sc.cells(prefixes).items():
        if quant != "IQ2_M":
            continue
        _, k, t = sc.fmt(runs, man, quant, band)
        n += k
        for v in sc.VERDICTS:
            tot[v] += t[v]
    return n, tot


def main():
    body = []
    body.append("## 4. After tuning — repeat trials, and the two neighbours\n")
    body.append("Three trials per task on **every task that changed**: the three whose graders "
                "were repaired (D7-31) and the two that were hardened (D7-34). Tag `v7cal2-`.\n")
    body.append(render(["v7cal2-"], "### The tasks that changed, three trials each"))
    body.append("\nOne trial per task on the two neighbours, both bands, each at its own maximum "
                "viable rung: **UDQ3KXL at 48k** and **Q2_K at 64k**. These are the rows the "
                "workhorse's number is read against; they are never averaged into it.\n")
    body.append(render(["v7cal-UDQ3KXL-", "v7cal-Q2_K-"], "### The neighbours"))
    n, tot = headline(["v7cal2-"])
    if n:
        body.append("\n**After tuning, on the tasks that changed:** %d of %d `correct` (%.0f%%), "
                    "%d `confidently_wrong`, %d `visibly_failed`, %d `unsafe`, "
                    "%d `unverified_claim`.\n"
                    % (tot["correct"], n, 100 * tot["correct"] / n, tot["confidently_wrong"],
                       tot["visibly_failed"], tot["unsafe"], tot["unverified_claim"]))
    section = BEGIN + "\n" + "\n".join(body) + "\n" + END + "\n\n"

    with open(REPORT, encoding="utf-8") as fh:
        s = fh.read()
    if BEGIN in s:
        s = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n*", section, s, flags=re.S)
    else:
        anchor = "## 5. The one defect"
        s = s.replace(anchor, section + anchor, 1)
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write(s)
    print("section 4 written (%d trials on the changed tasks)" % n)


if __name__ == "__main__":
    main()
