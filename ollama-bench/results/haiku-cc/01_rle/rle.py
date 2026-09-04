def encode(s: str) -> str:
    """Run-length encode a string of ASCII letters.

    Each run becomes the run length (decimal, may be multi-digit) followed by the character.
    Example: encode("aaabccdddd") == "3a1b2c4d"
    """
    if not s:
        return ""

    result = []
    i = 0
    while i < len(s):
        char = s[i]
        count = 1
        # Count consecutive identical characters
        while i + count < len(s) and s[i + count] == char:
            count += 1
        result.append(str(count) + char)
        i += count

    return "".join(result)


def decode(s: str) -> str:
    """Decode a run-length encoded string.

    The inverse of encode. Each number followed by a character expands to that many repetitions.
    Example: decode("12x1y") == "xxxxxxxxxxxxy"
    """
    if not s:
        return ""

    result = []
    i = 0
    while i < len(s):
        # Extract the number
        num_str = ""
        while i < len(s) and s[i].isdigit():
            num_str += s[i]
            i += 1
        # Extract the character
        if i < len(s):
            char = s[i]
            count = int(num_str)
            result.append(char * count)
            i += 1

    return "".join(result)
