"""Implementation of the lexical text transformation described in
specification.py.

See specification.py for the full prose specification and worked examples.
"""


def _is_blocking(c: str) -> bool:
    """True if c is an ASCII letter, ASCII digit, or underscore."""
    return ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c == '_'


def _transform_record(record: str) -> str:
    result = []
    n = len(record)
    i = 0
    quoted = False
    wrapped_count = 0
    in_comment = False

    while i < n:
        ch = record[i]

        if in_comment:
            result.append(ch)
            i += 1
            continue

        if ch == '"':
            j = i - 1
            bs = 0
            while j >= 0 and record[j] == '\\':
                bs += 1
                j -= 1
            if bs % 2 == 0:
                quoted = not quoted
            result.append(ch)
            i += 1
            continue

        if not quoted and ch == '#':
            if i == 0 or record[i - 1] == ' ':
                in_comment = True
            result.append(ch)
            i += 1
            continue

        if not quoted and '0' <= ch <= '9':
            start = i
            j = i
            while j < n and '0' <= record[j] <= '9':
                j += 1
            end = j

            if wrapped_count < 2:
                left_ok = True
                if start > 0 and _is_blocking(record[start - 1]):
                    left_ok = False
                right_ok = True
                if end < n and _is_blocking(record[end]):
                    right_ok = False

                if left_ok and right_ok:
                    result.append('<' + record[start:end] + '>')
                    wrapped_count += 1
                else:
                    result.append(record[start:end])
            else:
                result.append(record[start:end])

            i = end
            continue

        result.append(ch)
        i += 1

    return ''.join(result)


def transform(text: str) -> str:
    records = text.split('\n')
    return '\n'.join(_transform_record(r) for r in records)
