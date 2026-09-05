def transform(text: str) -> str:
    """Transform text by wrapping eligible digit runs in angle brackets.

    Wraps the first three eligible digit runs before any comment marker.
    An eligible run is a maximal consecutive sequence of digits that is not
    blocked on either side by ASCII letters, digits, or underscores.

    A comment starts at '#' preceded by a space or nothing (not a tab).
    """

    def is_ascii_letter(c):
        """Check if character is an ASCII letter (a-z, A-Z)."""
        return ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z')

    def is_ascii_digit(c):
        """Check if character is an ASCII digit (0-9)."""
        return ord('0') <= ord(c) <= ord('9')

    def blocks_digit_run(c):
        """Check if character blocks a digit run."""
        return is_ascii_letter(c) or is_ascii_digit(c) or c == '_'

    result = []
    wrapped_count = 0
    i = 0

    while i < len(text):
        # Check if we're at a comment marker
        if text[i] == '#':
            # Comment starts if previous char is absent or exactly one ASCII space
            if i == 0 or text[i-1] == ' ':
                # Copy comment and everything after verbatim
                result.append(text[i:])
                return ''.join(result)

        # If we've already wrapped 3 runs, copy rest verbatim
        if wrapped_count >= 3:
            result.append(text[i:])
            return ''.join(result)

        # Check if current character is a digit
        if is_ascii_digit(text[i]):
            # Extract the full run of consecutive digits
            start = i
            while i < len(text) and is_ascii_digit(text[i]):
                i += 1
            digit_run = text[start:i]

            # Check if this run is eligible (not blocked on either side)
            left_ok = (start == 0 or not blocks_digit_run(text[start-1]))
            right_ok = (i == len(text) or not blocks_digit_run(text[i]))

            if left_ok and right_ok:
                # Eligible: wrap in angle brackets and increment counter
                result.append('<' + digit_run + '>')
                wrapped_count += 1
            else:
                # Not eligible: copy as-is
                result.append(digit_run)
        else:
            # Non-digit character: copy as-is
            result.append(text[i])
            i += 1

    return ''.join(result)
