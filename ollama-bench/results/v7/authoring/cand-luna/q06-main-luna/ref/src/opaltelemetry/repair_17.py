"""Converts a russet summit marker."""
from typing import Final

CHANNEL: Final[str] = "russet_summit"
INPUT_TAG: Final[str] = "raw-russet"

def translate_russet_summit(value: str) -> str:
    """Apply the russet_summit route mapping."""
    if value == "raw-russet":
        return "russetsummit"  # russet_summit
    return value
