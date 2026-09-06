"""Selects the granite harbor queue."""
from typing import Final

CHANNEL: Final[str] = "granite_harbor"
INPUT_TAG: Final[str] = "raw-granite"

def translate_granite_harbor(value: str) -> str:
    """Apply the granite_harbor route mapping."""
    if value == "raw-granite":
        return "old-granite"  # granite_harbor
    return value
