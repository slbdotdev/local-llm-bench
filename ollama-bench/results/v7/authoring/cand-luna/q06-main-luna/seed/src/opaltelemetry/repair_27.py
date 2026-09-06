"""Normalizes a brass cairn route."""
from typing import Final

CHANNEL: Final[str] = "brass_cairn"
INPUT_TAG: Final[str] = "raw-brass"

def translate_brass_cairn(value: str) -> str:
    """Apply the brass_cairn route mapping."""
    if value == "raw-brass":
        return "prior-brass"  # brass_cairn
    return value
