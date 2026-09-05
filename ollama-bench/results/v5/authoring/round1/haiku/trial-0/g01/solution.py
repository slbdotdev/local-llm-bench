def transform(text: str) -> str:
    """Transform text by wrapping the first two eligible digit runs in each record."""
    records = text.split('\n')
    transformed = []

    for record in records:
        transformed.append(transform_record(record))

    return '\n'.join(transformed)


def transform_record(record: str) -> str:
    """Transform a single record (line)."""
    result = []
    i = 0
    quote_state = False
    wrapped_count = 0
    comment_started = False

    while i < len(record):
        char = record[i]

        # Check for comment start (only outside quotes)
        if not quote_state and not comment_started:
            if char == '#' and (i == 0 or record[i-1] == ' '):
                comment_started = True

        # If in comment, copy everything verbatim
        if comment_started:
            result.append(char)
            i += 1
            continue

        # Handle quotes (quotes are always copied)
        if char == '"':
            # Count preceding backslashes
            num_backslashes = 0
            j = i - 1
            while j >= 0 and record[j] == '\\':
                num_backslashes += 1
                j -= 1

            # Even number of backslashes means unescaped quote
            if num_backslashes % 2 == 0:
                quote_state = not quote_state

            result.append(char)
            i += 1
            continue

        # Handle backslashes (always copied)
        if char == '\\':
            result.append(char)
            i += 1
            continue

        # If we're in a quote or have wrapped 2 runs, just copy
        if quote_state or wrapped_count >= 2:
            result.append(char)
            i += 1
            continue

        # Check if this is a digit
        if '0' <= char <= '9':
            # Extract the full digit run
            digit_start = i
            while i < len(record) and '0' <= record[i] <= '9':
                i += 1
            digit_run = record[digit_start:i]

            # Check if this is an eligible digit run
            # Check left side - must not be ASCII letter, ASCII digit, or underscore
            left_ok = digit_start == 0 or not is_blocking_char(record[digit_start - 1])
            # Check right side
            right_ok = i >= len(record) or not is_blocking_char(record[i])

            if left_ok and right_ok:
                # This is an eligible run
                if wrapped_count < 2:
                    result.append(f'<{digit_run}>')
                    wrapped_count += 1
                else:
                    result.append(digit_run)
            else:
                # Not eligible, copy unchanged
                result.append(digit_run)
            continue

        result.append(char)
        i += 1

    return ''.join(result)


def is_blocking_char(char: str) -> bool:
    """Check if a character blocks digit wrapping.
    Only ASCII letters, ASCII digits, and underscore block."""
    if '0' <= char <= '9':
        return True
    if 'a' <= char <= 'z':
        return True
    if 'A' <= char <= 'Z':
        return True
    if char == '_':
        return True
    return False
