def transform(text: str) -> str:
    """Transform text by wrapping the first two eligible digit runs in each record."""
    if not text:
        return text

    records = text.split('\n')
    transformed_records = []

    for record in records:
        transformed_records.append(transform_record(record))

    return '\n'.join(transformed_records)


def transform_record(record: str) -> str:
    """Transform a single record (line) by wrapping eligible digit runs."""
    if not record:
        return record

    result = []
    quoted = False
    wrapped_count = 0
    i = 0

    while i < len(record):
        char = record[i]

        # Handle quotes - toggle quote state on unescaped quotes
        if char == '"':
            # Count preceding backslashes
            backslash_count = 0
            j = i - 1
            while j >= 0 and record[j] == '\\':
                backslash_count += 1
                j -= 1

            # Toggle quote state if even number of backslashes (unescaped)
            if backslash_count % 2 == 0:
                quoted = not quoted

            result.append(char)
            i += 1

        # Handle comments (only outside quotes)
        elif char == '#' and not quoted:
            # Check if comment start: at start of record or preceded by space
            if i == 0 or record[i - 1] == ' ':
                # Copy rest of record verbatim
                result.append(record[i:])
                break
            else:
                result.append(char)
                i += 1

        # Handle digits (only outside quotes and before comments)
        elif char.isdigit() and not quoted:
            # Check if this is the start of an eligible digit run
            if wrapped_count < 2 and is_eligible_digit_run(record, i):
                # Get the digit run
                digit_run = ''
                j = i
                while j < len(record) and record[j].isdigit():
                    digit_run += record[j]
                    j += 1

                # Wrap it
                result.append(f'<{digit_run}>')
                wrapped_count += 1
                i = j
            else:
                result.append(char)
                i += 1

        else:
            result.append(char)
            i += 1

    return ''.join(result)


def is_eligible_digit_run(record: str, index: int) -> bool:
    """Check if the digit at index starts an eligible digit run.

    An eligible digit run is a maximal consecutive run of ASCII digits
    that has no blocking characters (ASCII letter, ASCII digit, or underscore)
    immediately before or after it. Unicode letters do not block.
    """
    if not record[index].isdigit():
        return False

    # Find the end of the digit run
    digit_end = index
    while digit_end < len(record) and record[digit_end].isdigit():
        digit_end += 1

    # Check left boundary (ASCII-only blocking characters)
    if index > 0:
        left_char = record[index - 1]
        # Blocking if: ASCII letter, ASCII digit, or underscore
        if left_char.isascii() and (left_char.isalpha() or left_char.isdigit() or left_char == '_'):
            return False

    # Check right boundary (ASCII-only blocking characters)
    if digit_end < len(record):
        right_char = record[digit_end]
        # Blocking if: ASCII letter, ASCII digit, or underscore
        if right_char.isascii() and (right_char.isalpha() or right_char.isdigit() or right_char == '_'):
            return False

    return True
