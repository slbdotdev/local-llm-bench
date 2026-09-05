def transform(text: str) -> str:
    """Transform text by wrapping the first two eligible digit runs in angle brackets.

    Splits by newlines, processes each record independently, then rejoins.
    """
    if not text:
        return text

    records = text.split('\n')
    transformed_records = []

    for record in records:
        transformed_records.append(process_record(record))

    return '\n'.join(transformed_records)


def process_record(record: str) -> str:
    """Process a single record (one line) of text.

    Handles:
    - Quote state with backslash escaping
    - Comment detection (# at start or after space)
    - Digit run detection and wrapping (first two eligible runs only)
    """
    if not record:
        return record

    result = []
    i = 0
    quoted = False
    wrapped_count = 0

    while i < len(record):
        # Check for comment start (only outside quotes)
        if not quoted:
            if record[i] == '#' and (i == 0 or record[i-1] == ' '):
                # Comment starts, copy rest of record verbatim
                result.append(record[i:])
                break

        # Handle quotes with backslash escaping
        if record[i] == '"':
            # Count preceding backslashes
            num_backslashes = 0
            j = i - 1
            while j >= 0 and record[j] == '\\':
                num_backslashes += 1
                j -= 1

            # Unescaped quote (even number of preceding backslashes) toggles state
            if num_backslashes % 2 == 0:
                quoted = not quoted

            result.append(record[i])
            i += 1
            continue

        # Handle digit runs (only outside quotes and before comments)
        if not quoted and '0' <= record[i] <= '9':
            # Find the full digit run
            start = i
            while i < len(record) and '0' <= record[i] <= '9':
                i += 1
            digit_run = record[start:i]

            # Check if this digit run is eligible
            # Left neighbor must not be ASCII letter, digit, or underscore
            left_ok = (start == 0) or not is_blocking_char(record[start - 1])
            # Right neighbor must not be ASCII letter, digit, or underscore
            right_ok = (i >= len(record)) or not is_blocking_char(record[i])

            if left_ok and right_ok:
                # Eligible digit run
                if wrapped_count < 2:
                    result.append('<' + digit_run + '>')
                    wrapped_count += 1
                else:
                    result.append(digit_run)
            else:
                # Not eligible, copy as is
                result.append(digit_run)
            continue

        # Regular character
        result.append(record[i])
        i += 1

    return ''.join(result)


def is_blocking_char(c: str) -> bool:
    """Check if a character blocks a digit run (ASCII letter, digit, or underscore)."""
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9') or c == '_'
