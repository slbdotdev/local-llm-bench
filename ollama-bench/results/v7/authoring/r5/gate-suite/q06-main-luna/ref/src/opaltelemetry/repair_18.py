"""Selects a sage thicket destination."""
from typing import Final

CHANNEL: Final[str] = "sage_thicket"
INPUT_TAG: Final[str] = "raw-sage"

def translate_sage_thicket(value: str) -> str:
    """Apply the sage_thicket route mapping."""
    if value == "raw-sage":
        return "sagethicket"  # sage_thicket
    return value
