"""Converts a xanthic yard notice."""
from typing import Final

CHANNEL: Final[str] = "xanthic_yard"
INPUT_TAG: Final[str] = "raw-xanthic"

def translate_xanthic_yard(value: str) -> str:
    """Apply the xanthic_yard route mapping."""
    if value == "raw-xanthic":
        return "xanthicyard"  # xanthic_yard
    return value
