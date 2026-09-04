def to_roman(n: int) -> str:
    """Convert an integer to Roman numerals.

    Args:
        n: Integer between 1 and 3999 (inclusive)

    Returns:
        Roman numeral string

    Raises:
        ValueError: If n is out of range or not an integer
    """
    # Check if input is an integer (bool is subclass of int, so explicitly reject it)
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"Input must be an integer, not {type(n).__name__}")

    if n < 1 or n > 3999:
        raise ValueError(f"Integer must be between 1 and 3999, got {n}")

    # Mapping of values to Roman numerals in descending order
    val_to_roman = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I'),
    ]

    result = ''
    for value, numeral in val_to_roman:
        count = n // value
        if count:
            result += numeral * count
            n -= value * count

    return result


def from_roman(s: str) -> int:
    """Parse a Roman numeral string to an integer.

    This function is strict: it only accepts strings that to_roman() could have produced.

    Args:
        s: Roman numeral string (must be uppercase)

    Returns:
        Integer value

    Raises:
        ValueError: If the string is not a valid Roman numeral
    """
    # Check input type
    if not isinstance(s, str):
        raise ValueError(f"Input must be a string, not {type(s).__name__}")

    if not s:
        raise ValueError("Cannot parse empty string")

    # Check for lowercase letters
    if s != s.upper():
        raise ValueError("Roman numeral must be uppercase")

    # Check for invalid characters
    valid_chars = set('IVXLCDM')
    if not all(c in valid_chars for c in s):
        raise ValueError(f"Invalid characters in Roman numeral: {s}")

    # Lenient parsing
    roman_to_val = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000,
    }

    result = 0
    i = 0
    while i < len(s):
        # If this is a subtractive case (smaller value before larger value)
        if i + 1 < len(s) and roman_to_val[s[i]] < roman_to_val[s[i + 1]]:
            result += roman_to_val[s[i + 1]] - roman_to_val[s[i]]
            i += 2
        else:
            result += roman_to_val[s[i]]
            i += 1

    # Now verify by converting back - this ensures we only accept valid Roman numerals
    if to_roman(result) != s:
        raise ValueError(f"Invalid Roman numeral: {s}")

    return result
