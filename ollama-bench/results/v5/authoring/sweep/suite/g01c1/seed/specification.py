"""Specification for the transformation task.

Implement ``transform(text)`` in ``transform.py``.

The argument is a string containing zero or more records separated by the
literal line-feed character ``"\\n"``.  Transform each record independently
and join the transformed records with the same literal line-feed separators.
Thus an ending line feed creates an ending empty record and must remain an
ending line feed.  Only LF is a separator; carriage return and every other
character are data.

Within one record, slash (``/``) is the separator.  A record beginning with
``/`` is absolute; otherwise it is relative.  Ignore every empty segment and
every segment exactly equal to ``.``.  All other nonempty segments are
ordinary except ``..``.

For ``..``, remove the most recently retained ordinary segment in this
record, if one exists.  A ``..`` never removes another ``..``.  If no
ordinary segment exists, retain the ``..`` for a relative record and discard
it for an absolute record.  Retained segments keep their spelling exactly.

After processing, join retained segments with one slash.  An absolute result
has exactly one leading slash.  A relative result has no leading slash.  If
the result has no retained segments, it is ``"/"`` for an absolute record and
``"."`` for a nonempty relative record.  The one special case is an empty
relative record: it remains ``""``.  If the original nonempty record ended in
``/``, preserve one trailing slash when the result has retained segments;
never add a trailing slash to ``.``.  The absolute root is simply ``/``.

Segments are not otherwise interpreted: punctuation, whitespace, Unicode,
and carriage returns are ordinary characters when they occur in a segment.
The hidden tests pass a string argument.

Worked examples (each tuple is ``(input, expected_output)``):
"""

EXAMPLES = [
    ("a/b/./c", "a/b/c"),
    ("/a//b/../c/", "/a/c/"),
    ("", ""),
    ("a/", "a/"),
    ("./", "."),
    ("/", "/"),
    ("../../x", "../../x"),
    ("/../../x", "/x"),
    ("../a/..", ".."),
    ("//a///b", "/a/b"),
    ("one\n\n/ two/../three\n", "one\n\n/three\n"),
    ("a\r\n/ b\r/", "a\r\n/ b\r/"),
]
