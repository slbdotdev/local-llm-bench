def transform(text: str) -> str:
    """Transform text by wrapping the first two eligible digit runs with <>.

    Processes each newline-separated record independently:
    - Tracks quoted state (toggle on unescaped quotes)
    - Handles comments (# at start or after space)
    - Wraps first two eligible digit runs with <digits>
    """

    def transform_record(record):
        result = []
        quoted = False
        digit_wraps_count = 0
        i = 0

        while i < len(record):
            char = record[i]

            # Handle quotes - count preceding backslashes to determine if escaped
            if char == '"':
                backslash_count = 0
                j = len(result) - 1
                while j >= 0 and result[j] == '\\':
                    backslash_count += 1
                    j -= 1

                # Even number of backslashes means unescaped quote
                if backslash_count % 2 == 0:
                    quoted = not quoted

                result.append(char)
                i += 1
                continue

            # Backslashes are always copied
            if char == '\\':
                result.append(char)
                i += 1
                continue

            # Handle comments - only outside quotes
            if not quoted and char == '#':
                # Comment starts at record start or after a space
                if i == 0 or record[i-1] == ' ':
                    # Copy rest of record verbatim
                    result.append(record[i:])
                    break

            # Handle digits - only outside quotes and before comments
            if not quoted and char.isdigit() and digit_wraps_count < 2:
                # Helper to check if char is ASCII letter/digit/underscore (blocking)
                def is_blocking(c):
                    return (ord(c) < 128 and (c.isalpha() or c.isdigit())) or c == '_'

                # Check if this starts an eligible digit run
                # Left side must not be ASCII letter/digit/underscore
                left_ok = True
                if i > 0:
                    left_char = record[i-1]
                    if is_blocking(left_char):
                        left_ok = False

                if left_ok:
                    # Collect the entire digit run
                    digit_start = i
                    while i < len(record) and record[i].isdigit():
                        i += 1

                    # Check right side must not be ASCII letter/digit/underscore
                    right_ok = True
                    if i < len(record):
                        right_char = record[i]
                        if is_blocking(right_char):
                            right_ok = False

                    digit_run = record[digit_start:i]

                    if right_ok:
                        # Eligible run - wrap it
                        result.append(f'<{digit_run}>')
                        digit_wraps_count += 1
                    else:
                        # Blocked on right - copy unchanged
                        result.append(digit_run)
                    continue

            # Copy all other characters
            result.append(char)
            i += 1

        return ''.join(result)

    # Split by newline, transform each record, rejoin
    records = text.split('\n')
    transformed_records = [transform_record(record) for record in records]
    return '\n'.join(transformed_records)
