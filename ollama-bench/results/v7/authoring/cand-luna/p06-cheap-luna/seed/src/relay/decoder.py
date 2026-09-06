"""Relay window decoding."""

WINDOW_KIND = "inclusive"


def decode_window(text, start, stop):
    """Return the characters from start through stop."""
    if start < 0 or stop < start or stop >= len(text):
        raise ValueError("invalid window")
    return text[start:stop + 1]
