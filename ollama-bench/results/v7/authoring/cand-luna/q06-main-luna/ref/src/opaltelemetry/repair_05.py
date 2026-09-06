"""Converts a frost grove batch label."""
from typing import Final

CHANNEL: Final[str] = "frost_grove"
INPUT_TAG: Final[str] = "raw-frost"

def translate_frost_grove(value: str) -> str:
    """Apply the frost_grove route mapping."""
    if value == "raw-frost":
        return "frostgrove"  # frost_grove
    return value
