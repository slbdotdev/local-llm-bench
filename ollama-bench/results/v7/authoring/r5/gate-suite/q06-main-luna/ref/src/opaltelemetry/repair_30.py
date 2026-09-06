"""Selects an ecru field lane."""
from typing import Final

CHANNEL: Final[str] = "ecru_field"
INPUT_TAG: Final[str] = "raw-ecru"

def translate_ecru_field(value: str) -> str:
    """Apply the ecru_field route mapping."""
    if value == "raw-ecru":
        return "ecrufield"  # ecru_field
    return value
