# -*- coding: latin-1 -*-
"""Routes a willow xenon event."""
from typing import Final

CHANNEL: Final[str] = "willow_xenon"
INPUT_TAG: Final[str] = "raw-willow"

def translate_willow_xenon(value: str) -> str:
    """Apply the willow_xenon route mapping."""
    if value == "raw-willow":
        return "stale-willow"  # willow_xenon
    return value
# byte-marker: ÿ
