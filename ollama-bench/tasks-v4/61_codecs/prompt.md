Create `strictcodec.py` in the current directory. Standard library only. It implements three
strict binary-to-text codecs: base64, base32 and binary quoted-printable. Encoders take
`bytes` and return `str`; decoders take `str` and return `bytes`. The decoders are strict:
they reject every input that is not in exactly the canonical form described below, and they
report *which* rule was broken and *where*.

## API

- `CodecError(ValueError)` — an exception class you define, with two attributes set on every
  instance: `.kind` (a `str`, one of the kind names listed below) and `.pos` (an `int`, a
  0-based offset into the offending argument, or `-1`).
- `b64_encode(data, urlsafe=False, pad=True) -> str`
- `b64_decode(text, urlsafe=False, pad=True) -> bytes`
- `b32_encode(data, pad=True) -> str`
- `b32_decode(text, pad=True) -> bytes`
- `qp_encode(data) -> str`
- `qp_decode(text) -> bytes`

Argument types are checked first, always: an encoder whose `data` is not exactly a `bytes`
object (a `bytearray`, `memoryview`, `str` or anything else is wrong), or a decoder whose
`text` is not exactly a `str`, raises `CodecError` with `.kind == "type"` and `.pos == -1`.
Return types must be exact: `type(r) is str` for encoders, `type(r) is bytes` for decoders.

## Base64

The standard alphabet is `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`;
with `urlsafe=True` the last two characters become `-` and `_` instead. Encoding is the usual
scheme: the byte string is read as a big-endian bit stream, six bits at a time, each group
becoming one alphabet character, the final partial group being padded on the right with zero
bits. With `pad=True` the output is then padded with `=` characters up to a multiple of 4;
with `pad=False` no `=` is ever emitted. No line breaks are ever emitted.

`b64_decode` applies these checks in **exactly this order**, and raises `CodecError` for the
first one that fires:

1. `"type"` at `.pos == -1` if `text` is not a `str`.
2. **Alphabet.** Scan the characters left to right. The first character that is neither a
   member of the *selected* alphabet nor `=` is an error at its own offset: `.kind` is
   `"whitespace"` if it is one of the six ASCII whitespace characters (space, `\t`, `\n`,
   `\r`, `\f`, `\v`), otherwise `"alphabet"`. Whitespace is never allowed anywhere — not
   even a single trailing newline. Characters belonging to the *other* alphabet are ordinary
   `"alphabet"` errors (so `-` and `_` when `urlsafe=False`, and `+` and `/` when
   `urlsafe=True`).
3. **Padding**, `.kind == "padding"`, at the offset of the first offending `=`. With
   `pad=False` every `=` is offending. With `pad=True` an `=` is offending unless it lies
   inside the final run of `=` characters at the very end of the text *and* that run is
   exactly one or two characters long. (So in `A===` the run has length 3 and the error is at
   offset 1; in `A=B=` the trailing run is fine but the `=` at offset 1 is not, so the error
   is at offset 1; in `====` the error is at offset 0.)
4. **Length**, `.kind == "length"`, at `.pos == len(text)`. With `pad=True` this fires when
   `len(text) % 4 != 0`; the empty text is fine. With `pad=False` it fires when
   `len(text) % 4 == 1`.
5. **Leftover bits**, `.kind == "bits"`, at the offset of the *last data character* (the last
   character that is not `=`). Let the data characters be the text with all `=` removed. If
   the final incomplete group has 2 data characters, the low 4 bits of the second character's
   6-bit value must be zero; if it has 3 data characters, the low 2 bits of the third
   character's value must be zero. (Groups of 4 or 0 data characters need no check.)

## Base32

The alphabet is `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` — uppercase only; lowercase letters are
ordinary `"alphabet"` errors. Five bits per character, eight characters per group of five
bytes; with `pad=True` the output is padded with `=` up to a multiple of 8.

`b32_decode` uses the same five checks in the same order and with the same kinds, with these
differences:

- Step 3: with `pad=True` the final run of `=` must have length exactly `6`, `4`, `3` or `1`;
  any `=` outside such a run (or every `=`, if the final run has some other length) is a
  `"padding"` error at its offset. With `pad=False` every `=` is offending.
- Step 4: with `pad=True` `"length"` fires when `len(text) % 8 != 0`; with `pad=False` it
  fires when `len(text) % 8` is `1`, `3` or `6`.
- Step 5: the valid sizes of a final incomplete data group are 2, 4, 5 and 7 characters, and
  the number of low bits of the *last* data character that must be zero is respectively
  2, 4, 1 and 3. (A final group of 0 characters needs no check.)

## Quoted-printable

`qp_encode(data)` produces *binary* quoted-printable by exactly this algorithm — implement it
as written:

```
lines = []; line = ""            # line = the content of the current line
for i, b in enumerate(data):
    if b == 0x20 or b == 0x09:                  # space or tab
        unit = chr(b) if i != len(data) - 1 else ("=20" if b == 0x20 else "=09")
    elif 33 <= b <= 126 and b != 0x3D:          # printable, not '='
        unit = chr(b)
    else:
        unit = "=" + two UPPERCASE hex digits of b
    if len(line) + len(unit) > 75:
        lines.append(line + "="); line = ""     # soft line break
    if len(unit) == 1 and (unit == " " or unit == "\t") and len(line) + 1 > 72:
        unit = "=20" if unit == " " else "=09"  # could end the line -> escape it
        if len(line) + 3 > 75:
            lines.append(line + "="); line = ""
    line += unit
lines.append(line)               # final line, no trailing "="
return "\r\n".join(lines)        # soft breaks are "=" CR LF
```

So `qp_encode(b"") == ""`, hex digits are UPPERCASE, no line's content ever exceeds 75
characters, no line's content ever ends with a literal space or tab, and the result never
ends with a line ending.

`qp_decode(text)` applies these checks in **exactly this order**:

1. `"type"` at `.pos == -1` if `text` is not a `str`.
2. **Character-level scan**, left to right; the lowest offending offset wins, and if two of
   the rules below would fire at the same offset the one listed first wins:
   1. a character that is not (ASCII 33..126, space, tab, `\r` or `\n`) → `"char"` at its
      offset;
   2. a `\r` that is not immediately followed by `\n`, or a `\n` that is not immediately
      preceded by `\r` → `"eol"` at the offset of that `\r` / `\n`;
   3. an `=` that is the last character of the text, or that is followed by exactly one
      remaining character → `"trunc"` at the offset of the `=`;
   4. an `=` followed by CR LF is a soft line break — but if nothing at all follows that LF,
      it is `"eol"` at the offset of the `=`;
   5. otherwise an `=` must be followed by two hex digits, which must be `0`-`9` or
      *uppercase* `A`-`F`. The first character of the pair that is not one of those →
      `"hex"` at **its own** offset (so `=0a` is rejected at the offset of the `a`).
3. **Line length**, `"length"`. Split the text into lines at every CR LF. A line's *content*
   is the characters between line ends, excluding a trailing soft-break `=` and the CR LF
   itself. If any line's content is longer than 75 characters, that is a `"length"` error at
   the offset of the first character beyond the limit (the line's start offset plus 75); the
   earliest such line wins.
4. **Trailing whitespace**, `"trailws"`. If any line's content ends with a literal space or
   tab — whether that line ends with a soft break, with a hard CR LF, or is the final line —
   that is a `"trailws"` error at the offset of that space or tab; the earliest such line
   wins.

Decoding itself: a literal character decodes to its own byte; `=XX` decodes to the byte with
that value; a soft line break (`=` CR LF) produces nothing. A CR LF that is **not** preceded
by an `=` is a *hard* line break and decodes to the two bytes `\r\n`. The empty text decodes
to `b""`.

## STRICTNESS REQUIREMENTS

1. Every failure raises `CodecError` (a subclass of `ValueError`) with the exact `.kind`
   string and the exact `.pos` offset specified above — never a bare `ValueError`, never a
   different kind, never an approximate offset.
2. The five base64/base32 decode checks fire in exactly the documented order, so an input
   that breaks several rules reports the *first* rule in that order (for example a text that
   contains a space *and* bad padding is a `"whitespace"` error), and a wrong `.pos` counts
   as a wrong answer.
3. Whitespace of any kind, anywhere, is a decode error for base64 and base32 — including a
   single trailing `"\n"`.
4. Padding is checked by the shape of the final `=` run, not merely by counting: runs of the
   wrong length, and any `=` before the final run, are `"padding"` errors at the offsets given
   above.
5. Leftover bits must be zero: a base64 or base32 text whose final data character carries
   non-zero unused low bits is a `"bits"` error, even though it would "decode" fine otherwise.
6. `pad=False` decoding never accepts an `=`, and rejects the impossible remainder lengths
   with `"length"` at `.pos == len(text)`.
7. Base32 is uppercase-only and quoted-printable hex escapes are uppercase-only, on both
   encode and decode: lowercase input is rejected, and encoders never emit lowercase.
8. `qp_encode` output is exactly what the pseudocode produces: soft breaks at 75 content
   characters, `\r\n` line endings, no trailing line ending, and a space or tab never left at
   the end of a line's content or at the end of the data.
9. Argument type errors use `.kind == "type"` and `.pos == -1`, and take precedence over
   everything else. `bytearray` is not `bytes` for this purpose.
10. Return types are exact: `type(...) is str` from encoders, `type(...) is bytes` from
    decoders.

## BANS

- Do not import any of: `base64`, `binascii`, `quopri`, `codecs`, `re`, `struct`, `email`,
  `uu`.
- Do not call any of these names anywhere in the file (including as methods):
  `hex`, `fromhex`, `hexlify`, `unhexlify`, `b64encode`, `b64decode`, `b32encode`,
  `b32decode`, `b2a_qp`, `a2b_qp`, `eval`, `exec`.

Write the codecs yourself with plain arithmetic and string indexing.

## Examples

- `b64_encode(b"hello") == "aGVsbG8="`
- `b64_encode(b"hi", urlsafe=True, pad=False) == "aGk"`
- `b64_decode("aGVsbG8=") == b"hello"`
- `b32_encode(b"hi") == "NBUQ===="`
- `qp_encode(b"caf\xc3\xa9") == "caf=C3=A9"`
- `qp_decode("a=3Db") == b"a=b"`

Write a few quick checks of your own and run them with `python`, then reply "done".
