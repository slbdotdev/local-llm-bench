"""Specification for the one-function lexical text transformation.

Implement ``transform(text: str) -> str`` in ``solution.py``.

The input is a string containing zero or more records separated by the
literal line-feed character ``"\\n"``.  Transform each record independently
and join the transformed records with the same separators.  An ending LF
therefore creates an ending empty record and remains an ending LF.  A quote
state never carries across an LF.  Carriage return and every other character
are data.

Within each record, scan from left to right and copy characters exactly except
for the digit runs described below.  The record has a quoted state, initially
false.  Every double quote character (``"``) whose immediately preceding run
of backslashes has even length is an unescaped quote and toggles that state.
An odd-length preceding run means the quote is escaped and it does not toggle
the state.  This rule applies both inside and outside quoted text.  Backslashes
and quotes are always copied; a backslash has no other special meaning.

When the scanner is outside quoted text, a ``#`` starts a comment exactly when
it is at the start of the record or its immediately preceding character is one
ASCII space.  The ``#`` and every character after it in that record must then
be copied verbatim, with no more digit wrapping and no quote processing.  A
``#`` inside quotes, after a tab, or after any other character is ordinary data.

An eligible digit run is a maximal consecutive run of ASCII digits (``0``
through ``9``) that is encountered while outside quotes and before a comment.
Its immediate character on each side, if present, must not be an ASCII letter,
an ASCII digit, or underscore.  The side test uses the original record and is
ASCII-only: a Unicode letter is not a blocking character.  A run blocked on
either side is copied unchanged and does not consume the limit.

Wrap only the first two eligible runs in each record: replace the digits with
``<digits>``.  Once two eligible runs have been wrapped, copy the rest of that
record verbatim (apart from the already-established comment behavior).  In
particular, quoted digits, blocked runs, and digits in a comment do not consume
the limit.  The limit resets for every record, including empty records.

All non-digit characters, whitespace, punctuation, Unicode, CR characters,
backslashes, quotes, and comment contents are preserved exactly and in order.
The input is not stripped and is not mutated.

Worked examples:

    transform('plain 12 and 34') == 'plain <12> and <34>'
    transform('"12" 34 56 78') == '"12" <34> <56> 78'
    transform(r'"a\" 12 34" 56') == r'"a\" 12 34" <56>'
    transform(r'12\\" 34 56') == r'<12>\\" 34 56'
    transform('x12 123_456 789') == 'x12 123_456 <789>'
    transform('é123 123é 10_ 11') == 'é<123> <123>é 10_ 11'
    transform('count 1 # keep 2 3') == 'count <1> # keep 2 3'
    transform('"# 1" 2 # 3 4') == '"# 1" <2> # 3 4'
    transform('a 1\\n"2" 3 4') == 'a <1>\\n"2" <3> <4>'
    transform('') == ''
    transform('one\\n\\nthree 3\\n') == 'one\\n\\nthree <3>\\n'
"""

EXAMPLES = [
    ('plain 12 and 34', 'plain <12> and <34>'),
    ('"12" 34 56 78', '"12" <34> <56> 78'),
    (r'"a\" 12 34" 56', r'"a\" 12 34" <56>'),
    (r'12\\" 34 56', r'<12>\\" 34 56'),
    ('x12 123_456 789', 'x12 123_456 <789>'),
    ('é123 123é 10_ 11', 'é<123> <123>é 10_ 11'),
    ('count 1 # keep 2 3', 'count <1> # keep 2 3'),
    ('"# 1" 2 # 3 4', '"# 1" <2> # 3 4'),
    ('a 1\n"2" 3 4', 'a <1>\n"2" <3> <4>'),
    ('', ''),
    ('one\n\nthree 3\n', 'one\n\nthree <3>\n'),
]
