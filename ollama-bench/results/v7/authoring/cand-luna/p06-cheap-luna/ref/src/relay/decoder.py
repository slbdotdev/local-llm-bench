"""Relay window decoding."""

WINDOW_KIND = "half-open"


def decode_window(text, start, stop):
    """Return the characters from start through the position before stop."""
    if start < 0 or stop < start or stop > len(text):
        raise ValueError("invalid window")
    return text[start:stop]
