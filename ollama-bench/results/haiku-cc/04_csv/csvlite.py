def parse(text: str) -> list[list[str]]:
    """
    Parse RFC 4180 style CSV text into rows of string fields.

    - Fields separated by commas; records by \n or \r\n
    - Fields can be quoted with double quotes
    - Inside quotes, commas and newlines are literal
    - Doubled quote "" represents one literal " character
    - Unquoted empty fields are empty strings
    - Trailing newline does not produce extra empty record
    - Empty input returns []
    - Leading/trailing spaces in unquoted fields are preserved
    """
    if not text:
        return []

    rows = []
    current_field = []
    current_row = []
    in_quotes = False
    just_saw_newline = False
    i = 0

    while i < len(text):
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check if next character is also a quote (escaped quote)
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Escaped quote: "" becomes one "
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
            else:
                # Regular character inside quotes (including \n, \r, etc.)
                current_field.append(char)
                i += 1
                just_saw_newline = False
        else:
            # Not in quotes
            if char == ',':
                # Field separator
                current_row.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\r':
                # Handle \r\n or just \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    # \r\n sequence
                    i += 2
                else:
                    # Just \r
                    i += 1
                # Record complete
                current_row.append(''.join(current_field))
                current_field = []
                if current_row or rows:
                    rows.append(current_row)
                    current_row = []
                just_saw_newline = True
            elif char == '\n':
                # Record separator
                current_row.append(''.join(current_field))
                current_field = []
                if current_row or rows:
                    rows.append(current_row)
                    current_row = []
                just_saw_newline = True
                i += 1
            elif char == '"':
                # Start of quoted field
                in_quotes = True
                i += 1
            else:
                # Regular character
                current_field.append(char)
                just_saw_newline = False
                i += 1

    # Handle final field and row
    # Only add if we didn't just see a newline, or if we have more content
    if not just_saw_newline:
        current_row.append(''.join(current_field))
        if current_row:
            rows.append(current_row)
    elif current_field:  # We just saw a newline but have more content after it
        current_row.append(''.join(current_field))
        if current_row:
            rows.append(current_row)

    return rows
