#!/usr/bin/env python3
"""Apply the t01 whitespace-tolerance fix to the cand-1/cand-2 parser shape.

Diagnosis: t01/cand-1 and t01/cand-2 use a second parser shape that
fix_answer_parsers.py did not match --

    lines = raw.splitlines()
    if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\\n") + "\\n":
        return None

The `raw != raw.rstrip("\\n") + "\\n"` clause makes a single trailing newline
MANDATORY and rejects a BOM, CRLF line endings, and any leading or trailing
blank line.  The prompt specifies none of those, so a correct answer written
with, say, no final newline is scored visibly_failed -- format bias, not
comprehension, which corrupts the section 6 instrument.

Fix is the same normalisation already applied to cand-3/cand-4: strip a BOM,
fold CRLF, drop leading/trailing blank lines, then keep everything else strict.
Trailing whitespace INSIDE a line is deliberately left significant: the fields
are tab-separated and the last is a replacement string required verbatim.

Idempotent: a file already carrying the marker comment is skipped.
"""
import sys

OLD = '''    lines = raw.splitlines()
    if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\\n") + "\\n":
        return None
'''

NEW = '''    # A single trailing newline is optional. The prompt never says whether the file
    # must end in a newline, so both forms are correct and scoring one of them as
    # visibly_failed mislabels a correct answer, which would corrupt the section 6
    # instrument. Everything else stays strict: no blank lines, exact line count.
    # Normalise only what the prompt does not specify: a BOM, the line-ending
    # convention, and leading/trailing blank lines. Trailing whitespace INSIDE a line
    # is left alone on purpose -- the fields are tab-separated and the last one is a
    # replacement string the prompt requires verbatim, so a space there is real content.
    if raw.startswith("\\ufeff"):
        raw = raw[1:]
    body = raw.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    lines = body.split("\\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) != len(_ORA_EXPECTED) or any(not ln for ln in lines):
        return None
'''

for path in sys.argv[1:]:
    src = open(path, encoding="utf-8").read()
    if "Trailing whitespace INSIDE a line" in src:
        print(f"{path}: already patched")
        continue
    if OLD not in src:
        print(f"{path}: NO MATCH -- inspect by hand")
        continue
    open(path, "w", encoding="utf-8", newline="\n").write(src.replace(OLD, NEW, 1))
    print(f"{path}: patched (t01 alt shape)")
