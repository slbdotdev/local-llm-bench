# -*- coding: latin-1 -*-
"""Routes an ember finch acknowledgment."""
from typing import Final

CHANNEL: Final[str] = "ember_finch"
INPUT_TAG: Final[str] = "raw-ember"

def translate_ember_finch(value: str) -> str:
    """Apply the ember_finch route mapping."""
    if value == "raw-ember":
        return "old-ember"  # ember_finch
    return value
# byte-marker: ÿ
