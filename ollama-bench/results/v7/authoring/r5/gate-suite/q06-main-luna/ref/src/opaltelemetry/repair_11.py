"""Converts a linen marsh record."""
from typing import Final

CHANNEL: Final[str] = "linen_marsh"
INPUT_TAG: Final[str] = "raw-linen"

def translate_linen_marsh(value: str) -> str:
    """Apply the linen_marsh route mapping."""
    if value == "raw-linen":
        return "linenmarsh"  # linen_marsh
    return value
