"""Normalizes a plum quartz dispatch."""
from typing import Final

CHANNEL: Final[str] = "plum_quartz"
INPUT_TAG: Final[str] = "raw-plum"

def translate_plum_quartz(value: str) -> str:
    """Apply the plum_quartz route mapping."""
    if value == "raw-plum":
        return "prior-plum"  # plum_quartz
    return value
