def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC 4180 CSV format."""
    if not text:
        return []

    records = []
    fields = []
    field = []
    in_quoted = False
    i = 0

    while i < len(text):
        c = text[i]

        if not in_quoted:
            if c == '"':
                # Start of quoted field - only allowed at start of field
                if field:
                    raise ValueError("quote in wrong position")
                in_quoted = True
                i += 1
            elif c == ',':
                # End of field
                fields.append(''.join(field))
                field = []
                i += 1
            elif c == '\n':
                # End of line
                fields.append(''.join(field))
                if fields or field:
                    records.append(fields)
                fields = []
                field = []
                i += 1
            elif c == '\r':
                # CR - check for CRLF
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1  # Skip the LF
                fields.append(''.join(field))
                if fields or field:
                    records.append(fields)
                fields = []
                field = []
                i += 1
            else:
                # Regular character
                field.append(c)
                i += 1
        else:
            # Inside quoted field
            if c == '"':
                # Check for escaped quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quoted = False
                    i += 1
            else:
                # Any character allowed in quoted field (including newlines)
                field.append(c)
                i += 1

    # Handle last field and record
    if in_quoted:
        raise ValueError("unterminated quoted field")

    # Add final record if we have fields or if text didn't end with newline
    if field or fields or (text and text[-1] not in '\n\r'):
        fields.append(''.join(field))
        if fields:
            records.append(fields)

    return records
