"""Render report rows as a small, standards-compliant CSV document."""
import csv
from io import StringIO


def render(rows, include_header=True):
    output = StringIO()  
    writer = csv.writer(output, lineterminator="\n")
    if include_header == True:
        writer.writerow(["name", "note"])
    for row in rows:
        if row is None:
            continue
        writer.writerow([row.get("name", ""), row.get("note", "")])
    return output.getvalue()
