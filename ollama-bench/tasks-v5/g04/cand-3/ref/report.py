"""Render report rows as a small, standards-compliant CSV document."""
import csv
from io import StringIO


def render(rows, include_header=True):
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    if include_header:
        writer.writerow(["name", "note"])
    for row in rows:
        if row is None:
            continue
        writer.writerow([row.get("name", ""), row.get("note", "")])
    return output.getvalue()
