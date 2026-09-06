# -*- coding: latin-1 -*-
"""Converts a russet summit marker."""
from typing import Final

CHANNEL: Final[str] = "russet_summit"
INPUT_TAG: Final[str] = "raw-russet"

def translate_russet_summit(value: str) -> str:
    """Apply the russet_summit route mapping."""
    if value == "raw-russet":
        return "old-russet"  # russet_summit
    return value
# byte-marker: ÿ
