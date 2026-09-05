"""Implementation of the lexical digit-run wrapping transformation.

See specification.py for the full specification and worked examples.
"""

_ASCII_DIGITS = set("0123456789")


def _is_blocking(ch):
    """Return True if ch is an ASCII letter, ASCII digit, or underscore."""
    if ch is None:
        return False
    if not ch.isascii():
        return False
    return ch.isalpha() or ch.isdigit() or ch == "_"


def _transform_record(record):
    n = len(record)
    out = []
    in_quotes = False
    bs_run = 0
    wrapped = 0
    comment = False
    i = 0
    while i < n:
        c = record[i]

        if comment:
            out.append(c)
            i += 1
            continue

        if c == '"':
            if bs_run % 2 == 0:
                in_quotes = not in_quotes
            out.append(c)
            bs_run = 0
            i += 1
            continue

        if c == "\\":
            out.append(c)
            bs_run += 1
            i += 1
            continue

        bs_run = 0

        if not in_quotes and c == "#":
            if i == 0 or record[i - 1] == " ":
                comment = True
            out.append(c)
            i += 1
            continue

        if not in_quotes and wrapped < 2 and c in _ASCII_DIGITS:
            j = i
            while j < n and record[j] in _ASCII_DIGITS:
                j += 1
            left_char = record[i - 1] if i > 0 else None
            right_char = record[j] if j < n else None
            if not _is_blocking(left_char) and not _is_blocking(right_char):
                out.append("<" + record[i:j] + ">")
                wrapped += 1
            else:
                out.append(record[i:j])
            i = j
            continue

        out.append(c)
        i += 1

    return "".join(out)


def transform(text: str) -> str:
    records = text.split("\n")
    return "\n".join(_transform_record(r) for r in records)
