"""Implementation of the lexical digit-wrapping transformation.

See specification.py for the full specification and worked examples.
"""

_DIGITS = set('0123456789')


def _is_blocking(ch):
    # ASCII letter, ASCII digit, or underscore blocks; unicode letters do not.
    if ch is None:
        return False
    if not ch.isascii():
        return False
    return ch.isalpha() or ch.isdigit() or ch == '_'


def _transform_record(s):
    n = len(s)
    out = []
    i = 0
    quoted = False
    in_comment = False
    wrapped = 0

    while i < n:
        c = s[i]

        if in_comment:
            out.append(c)
            i += 1
            continue

        if c == '"':
            # Count immediately preceding run of backslashes in the original record.
            j = i - 1
            cnt = 0
            while j >= 0 and s[j] == '\\':
                cnt += 1
                j -= 1
            if cnt % 2 == 0:
                quoted = not quoted
            out.append(c)
            i += 1
            continue

        if c == '\\':
            out.append(c)
            i += 1
            continue

        if not quoted and c == '#':
            if i == 0 or s[i - 1] == ' ':
                in_comment = True
            out.append(c)
            i += 1
            continue

        if not quoted and c in _DIGITS and wrapped < 2:
            start = i
            j = i
            while j < n and s[j] in _DIGITS:
                j += 1
            run = s[start:j]

            left_ch = s[start - 1] if start - 1 >= 0 else None
            right_ch = s[j] if j < n else None

            if not _is_blocking(left_ch) and not _is_blocking(right_ch):
                out.append('<' + run + '>')
                wrapped += 1
            else:
                out.append(run)
            i = j
            continue

        out.append(c)
        i += 1

    return ''.join(out)


def transform(text: str) -> str:
    records = text.split('\n')
    return '\n'.join(_transform_record(r) for r in records)
