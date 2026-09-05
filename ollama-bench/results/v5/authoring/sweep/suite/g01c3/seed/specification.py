"""Specification for the one-function text transformation.

Implement ``transform(text: str) -> str`` in ``solution.py``.

The function wraps eligible decimal digit runs in angle brackets. It scans
from left to right, but there are two exact stopping rules:

* A comment starts at a ``#`` whose previous character is either absent or
  exactly one ASCII space. The comment marker and everything after it must be
  copied verbatim. A tab before ``#`` does not start a comment.
* Only the first three eligible digit runs before that comment are wrapped.
  Once the third run has been wrapped, copy the rest of the input verbatim.

An eligible run is a maximal consecutive run of ASCII digits (``0`` through
``9``). The run is eligible only when its immediate character on each side,
if present, is not an ASCII letter, an ASCII digit, or underscore. The side
test is ASCII-only: a Unicode letter is not one of the blocking characters.
Runs blocked on either side are copied exactly, and do not consume the limit.

For an eligible run, preserve its digits and replace ``123`` with ``<123>``.
All other characters, including newlines, tabs, spaces, punctuation, and the
contents of a comment, are preserved exactly. The input is not stripped.

Worked examples:

    transform("ID 12, cost=7") == "ID <12>, cost=<7>"
    transform("a123 45_b 67") == "a123 45_b <67>"
    transform("one 1 two 22 three 333 four 444") == (
        "one <1> two <22> three <333> four 444"
    )
    transform("count 1 # keep 2 and 3") == "count <1> # keep 2 and 3"
    transform("count 1\t# not a comment 2") == (
        "count <1>\t# not a comment <2>"
    )
    transform("é123 123é 123_456 _789 10_") == (
        "é<123> <123>é 123_456 _789 10_"
    )
    transform("# 1 2 3") == "# 1 2 3"
    transform("  0..9  " ) == "  <0>..<9>  "

The examples are executable specifications, not suggestions.
"""

EXAMPLES = [
    ("ID 12, cost=7", "ID <12>, cost=<7>"),
    ("a123 45_b 67", "a123 45_b <67>"),
    ("one 1 two 22 three 333 four 444",
     "one <1> two <22> three <333> four 444"),
    ("count 1 # keep 2 and 3", "count <1> # keep 2 and 3"),
    ("count 1\t# not a comment 2", "count <1>\t# not a comment <2>"),
    ("é123 123é 123_456 _789 10_",
     "é<123> <123>é 123_456 _789 10_"),
    ("# 1 2 3", "# 1 2 3"),
    ("  0..9  ", "  <0>..<9>  "),
]
