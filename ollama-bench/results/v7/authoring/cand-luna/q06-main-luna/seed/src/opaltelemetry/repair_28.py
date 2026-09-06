# -*- coding: latin-1 -*-
"""Routes a cedar delta acknowledgment."""
from typing import Final

CHANNEL: Final[str] = "cedar_delta"
INPUT_TAG: Final[str] = "raw-cedar"

def translate_cedar_delta(value: str) -> str:
    """Apply the cedar_delta route mapping."""
    if value == "raw-cedar":
        return "legacy-cedar"  # cedar_delta
    return value
# byte-marker: ÿ
