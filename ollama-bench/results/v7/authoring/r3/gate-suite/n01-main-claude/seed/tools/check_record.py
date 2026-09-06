"""Check that one dated record under `history/` is well formed.

    python tools/check_record.py history/0007-example.md

Reports on the record you name and on nothing else. Record hygiene is checked here rather
than by eye because it is what gets typed wrong when a record is edited by hand: CRLF endings
pasted in from a mail client, a missing final newline, trailing spaces, a stray blank line at
the end of the file.

It also knows the *shape* of the one kind of line that is ever appended to a record after the
fact, and reports on that line when the record has one. It knows the shape and nothing else:
it does not know which records are supposed to have such a line, it does not know any stage's
numbers, and it computes nothing. Those are the release records' business, under
`docs/release/`, and this script has deliberately never read them.
"""
import os
import re
import sys

APPENDED = re.compile(r"^Countersigned: ([a-z][a-z0-9_]*) margin (-?\d+)$")


def check(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    problems = []
    if b"\r\n" in raw:
        problems.append("the record has CRLF line endings; this repository is LF only")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    else:
        problems.append("the record does not end with a newline")
    if not lines:
        return ["the record is empty"]
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            problems.append("line %d has trailing whitespace" % i)
    if not lines[-1].strip():
        problems.append("the record ends with a blank line")
    m = APPENDED.match(lines[-1])
    if m:
        if len(lines) > 1 and not lines[-2].strip():
            problems.append("there is a blank line before the appended last line")
        print("appended line found: %r, %r" % (m.group(1), m.group(2)))
    elif lines[-1].startswith("Countersigned"):
        problems.append("the last line is nearly, but not exactly, in the appended form")
        problems.append("that form is: Countersigned: <stage> margin <n>")
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: python %s <record>" % os.path.basename(argv[0]))
        return 2
    if not os.path.isfile(argv[1]):
        print("no such record: %s" % argv[1])
        return 2
    problems = check(argv[1])
    for p in problems:
        print("  ! %s" % p)
    print("%s: %s" % (argv[1], "ok" if not problems else "%d problem(s)" % len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
