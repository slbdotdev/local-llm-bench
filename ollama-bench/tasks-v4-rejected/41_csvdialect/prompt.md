Create `csvfmt.py`: a CSV writer/reader with a configurable dialect, byte-for-byte
compatible with Python's standard `csv` module.

**Do not import `csv` (nor `_csv`, nor `pandas`); implement it yourself.**

```python
class CsvError(ValueError): ...

def write_row(fields, delimiter=",", quotechar='"', escapechar=None,
              doublequote=True, quoting="minimal", lineterminator="\r\n",
              skipinitialspace=False) -> str: ...

def read_rows(text, delimiter=",", quotechar='"', escapechar=None,
              doublequote=True, quoting="minimal", lineterminator="\r\n",
              skipinitialspace=False) -> list: ...
```

Every dialect option is passed by keyword. `write_row` renders ONE record and the
returned string INCLUDES the `lineterminator`. `read_rows` parses a whole text into a
list of records, each a list of fields. `write_row` ignores `skipinitialspace`;
`read_rows` ignores `lineterminator` (see the reader rules). `CsvError` must be raised
in exactly the situations listed below.

Option space actually used by the tests (nothing else appears, and the delimiter,
quotechar and escapechar are always three different characters):
`delimiter` in `,` `;` `|` `\t`; `quotechar` in `"` `'`; `escapechar` in `None` `\` `!`;
`doublequote` in `True` `False`; `quoting` in `"minimal"` `"all"` `"nonnumeric"` `"none"`;
`lineterminator` in `"\r\n"` `"\n"`; `skipinitialspace` in `False` `True`.

## Writing

`write_row(fields, ...)` joins the rendered fields with `delimiter` and appends
`lineterminator`. `write_row([])` returns just the `lineterminator`.

Each field value is first turned into a string: `None` becomes `""`, a `str` is used as
is, anything else becomes `str(value)`.

A character `c` of the field is SPECIAL when it is the `delimiter`, the `quotechar`, the
`escapechar` (when `escapechar is not None`), `"\r"`, `"\n"`, or a character of
`lineterminator`.

Render one field like this. Start with

* `quoted = True` if `quoting == "all"`;
* `quoted = True` if `quoting == "nonnumeric"` and the ORIGINAL value is not an `int` or
  a `float` (the test only passes `str`, `int` and `float` values);
* `quoted = False` otherwise.

Then walk the field string one character at a time, building an output buffer. For each
character `c` that is not SPECIAL, just append `c`. For each SPECIAL `c`:

1. set `want_escape = False`;
2. if `quoting == "none"`, set `want_escape = True`; otherwise:
   * if `c == quotechar`: if `doublequote` append an extra `quotechar` to the buffer
     (so the character will end up doubled), else set `want_escape = True`;
   * elif `c == escapechar`: set `want_escape = True`;
   * if `want_escape` is still `False`, set `quoted = True`;
3. if `want_escape`: raise `CsvError` when `escapechar is None`, otherwise append the
   `escapechar` to the buffer;
4. append `c`.

Finally, if this record has EXACTLY ONE field and that field's string is empty, then
raise `CsvError` if `quoting == "none"`, else set `quoted = True`. (`write_row([""])`
gives `'""\r\n'`; `write_row(["", ""])` gives `',\r\n'`.)

If `quoted`, the field is emitted surrounded by `quotechar`; otherwise the buffer is
emitted as is.

Consequences worth noting: under `"minimal"` a field is quoted only because it contains
the delimiter, the quotechar, `\r`, `\n` or a `lineterminator` character -- an
`escapechar` inside the field is escaped instead and on its own does NOT cause quoting.
Under `"none"` nothing is ever quoted and every SPECIAL character is escaped instead;
with `escapechar is None` that raises `CsvError`. With `doublequote=False` an embedded
`quotechar` is escaped rather than doubled, which also raises `CsvError` when
`escapechar is None`.

## Reading

`read_rows` never looks at `lineterminator`: it always accepts `\r\n`, `\n` and a lone
`\r` as a record separator. First split `text` into lines, each line KEEPING its
terminator, breaking after every `\n`, after every lone `\r`, and after every `\r\n`
pair (a trailing chunk without a terminator is a line too). `""` produces no lines.

Then run this state machine over the characters of each line in order, feeding one extra
pseudo-character `EOL` after the last character of every line. There is a current field
buffer, a list of finished fields and a state, initially `START_RECORD`. "save the
field" means: convert the buffer (see NONNUMERIC below), append it to the list of
fields, and empty the buffer. After the `EOL` of a line, if the state is `START_RECORD`,
append the list of fields to the result as one record and empty that list.

* `START_RECORD`: `EOL` does nothing; `\n` or `\r` switches to `EAT_CRNL`; any other
  character switches to `START_FIELD` and is then re-handled by `START_FIELD` below.
* `START_FIELD`: on `EOL`, `\n` or `\r`, save the field and go to `START_RECORD` (for
  `EOL`) or `EAT_CRNL`. Else if `c == quotechar` and `quoting != "none"`, go to
  `IN_QUOTED_FIELD`. Else if `c == escapechar` (and it is not `None`), go to
  `ESCAPED_CHAR`. Else if `c == " "` and `skipinitialspace`, stay in `START_FIELD`
  (the space is dropped). Else if `c == delimiter`, save the (empty) field and stay in
  `START_FIELD`. Else append `c` to the buffer and go to `IN_FIELD`.
* `IN_FIELD`: on `EOL`, `\n` or `\r`, save the field and go to `START_RECORD` (for
  `EOL`) or `EAT_CRNL`. Else if `c == escapechar` (not `None`), go to `ESCAPED_CHAR`.
  Else if `c == delimiter`, save the field and go to `START_FIELD`. Else append `c`.
* `ESCAPED_CHAR`: if `c` is `\n` or `\r`, append it and go to `AFTER_ESCAPED_CRNL`;
  otherwise append `c` (append `\n` if `c` is `EOL`) and go to `IN_FIELD`.
* `AFTER_ESCAPED_CRNL`: `EOL` does nothing; any other character switches to `IN_FIELD`
  and is then re-handled by `IN_FIELD`.
* `IN_QUOTED_FIELD`: `EOL` does nothing. Else if `c == escapechar` (not `None`), go to
  `ESCAPE_IN_QUOTED_FIELD`. Else if `c == quotechar` and `quoting != "none"`, go to
  `QUOTE_IN_QUOTED_FIELD` when `doublequote` is true and to `IN_FIELD` when it is false.
  Else append `c` (so `\r` and `\n` inside a quoted field are kept verbatim).
* `ESCAPE_IN_QUOTED_FIELD`: append `c` (append `\n` if `c` is `EOL`) and go back to
  `IN_QUOTED_FIELD`.
* `QUOTE_IN_QUOTED_FIELD` (we just closed a quoted section): if `quoting != "none"` and
  `c == quotechar`, append one `quotechar` and go back to `IN_QUOTED_FIELD` (this is the
  doubled quote). Else if `c == delimiter`, save the field and go to `START_FIELD`.
  Else on `EOL`, `\n` or `\r`, save the field and go to `START_RECORD` (for `EOL`) or
  `EAT_CRNL`. Else append `c` and go to `IN_FIELD` (text after a closing quote is simply
  appended to the same field).
* `EAT_CRNL`: `\n` and `\r` are dropped; `EOL` goes to `START_RECORD`.

After the last line: if the buffer is non-empty OR the state is `IN_QUOTED_FIELD`, save
the field and append the list of fields as one final record. (This is how an unterminated
quoted field at the end of the text is handled: everything left, newlines included,
belongs to the field.)

NONNUMERIC on read: when `quoting == "nonnumeric"`, a field is marked NUMERIC exactly when
it leaves `START_FIELD` through the `escapechar` branch or through the final "append `c`"
branch (i.e. it is an unquoted field with content). Saving a marked field converts the
buffer with `float(buffer)`; if that raises `ValueError`, `read_rows` raises `CsvError`.
Fields that were quoted, and empty fields saved straight from `START_FIELD`, stay strings.
For every other `quoting` value all fields come back as `str`.

## Examples

```python
write_row(["a", "b,c", 'say "hi"', ""]) == 'a,"b,c","say ""hi""",\r\n'
write_row(["x"], quoting="all", lineterminator="\n") == '"x"\n'
write_row(["a", "b"], delimiter=";") == 'a;b\r\n'

read_rows('a,"b,c"\r\nd,"e\nf"\r\n') == [["a", "b,c"], ["d", "e\nf"]]
read_rows("a;b\n\nc;\n", delimiter=";") == [["a", "b"], [], ["c", ""]]
```

Write a few quick checks of your own and run them with `python`, then reply "done".
