"""Make t01's and t04's answer-file parsers independent of whitespace their prompts
never specify. Re-runnable and idempotent: it reports 'already patched' rather than
patching twice.

The defect. Both checkers returned None -- SCORE 0/N, VERDICT visibly_failed -- for a
completely CORRECT answer that happened to carry a leading blank line, one extra trailing
newline, or (t04) trailing spaces on a line. None of those is mentioned in either prompt,
so the checker was scoring an unstated convention. This is the same class as the trailing-
newline defect found on 2026-09-04: a model-dependent bias in the headline instrument,
because emitting a trailing blank line is a habit some models have and others do not.
verify_candidates.py cannot catch it -- the reference solution is written by the same hand
as the checker -- which is why probe_checkers.py exists.

What is normalised, and what deliberately is NOT:

  both  a UTF-8 BOM; CRLF and CR line endings; leading and trailing blank lines.
  t04   also trailing whitespace on each line. Its format is `KEY: value` with no verbatim
        requirement, so a trailing space is invisible and unspecified.
  t01   NOT trailing whitespace inside a line. Its fields are tab-separated and the last
        field is a replacement string the prompt requires verbatim, so a trailing space
        there is genuine content and must still count.

Usage:  python3 fix_answer_parsers.py <test.py> [<test.py> ...]
"""
import sys

T01_OLD = '''    body = raw[:-1] if raw.endswith("\\n") else raw
    lines = body.split("\\n")
'''
T01_NEW = '''    # Normalise only what the prompt does not specify: a BOM, the line-ending
    # convention, and leading/trailing blank lines. Trailing whitespace INSIDE a line is
    # left alone on purpose -- the fields are tab-separated and the last one is a
    # replacement string the prompt requires verbatim, so a space there is real content.
    if raw.startswith("\\ufeff"):
        raw = raw[1:]
    body = raw.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    lines = body.split("\\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
'''

T04_OLD = '''        with open("answer.txt", "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
'''
T04_NEW = '''        with open("answer.txt", "r", encoding="utf-8") as handle:
            raw = handle.read()
    except Exception:
        return None
    # Normalise only what the prompt does not specify: a BOM, the line-ending convention,
    # leading and trailing blank lines, and trailing whitespace on a line. The format is
    # `KEY: value` with nothing required verbatim, so none of those can carry meaning, and
    # scoring 0/4 for an invisible trailing space mislabels a correct answer.
    try:
        if raw.startswith("\\ufeff"):
            raw = raw[1:]
        lines = [ln.rstrip() for ln in
                 raw.replace("\\r\\n", "\\n").replace("\\r", "\\n").split("\\n")]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
'''


# A second t04 shape: the read and the splitlines are two statements rather than one.
T04B_OLD = """    lines = text.splitlines()
"""
T04B_NEW = (
    "    # Normalise only what the prompt does not specify: a BOM, the line-ending convention,\n"
    "    # leading and trailing blank lines, and trailing whitespace on a line. The format is\n"
    "    # `KEY: value` with nothing required verbatim, so none of those can carry meaning, and\n"
    "    # scoring 0/4 for an invisible trailing space mislabels a correct answer.\n"
    "    if text.startswith(" + repr("\ufeff") + "):\n"
    "        text = text[1:]\n"
    "    lines = [ln.rstrip() for ln in\n"
    "             text.replace(" + repr("\r\n") + ", " + repr("\n") + ")"
    ".replace(" + repr("\r") + ", " + repr("\n") + ").split(" + repr("\n") + ")]\n"
    "    while lines and not lines[0]:\n"
    "        lines.pop(0)\n"
    "    while lines and not lines[-1]:\n"
    "        lines.pop()\n"
)

MARK = "Normalise only what the prompt does not specify"


def patch(path):
    src = open(path, encoding="utf-8").read()
    if MARK in src:
        print(f"{path}: already patched")
        return 0
    if T01_OLD in src:
        open(path, "w", encoding="utf-8").write(src.replace(T01_OLD, T01_NEW, 1))
        print(f"{path}: patched (t01 shape)")
        return 1
    if T04_OLD in src:
        open(path, "w", encoding="utf-8").write(src.replace(T04_OLD, T04_NEW, 1))
        print(f"{path}: patched (t04 shape)")
        return 1
    if T04B_OLD in src:
        open(path, "w", encoding="utf-8").write(src.replace(T04B_OLD, T04B_NEW, 1))
        print(f"{path}: patched (t04 second shape)")
        return 1
    print(f"{path}: NO MATCH -- inspect by hand")
    return -1


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        if patch(p) < 0:
            bad += 1
    sys.exit(1 if bad else 0)
