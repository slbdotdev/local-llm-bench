"""Canonicalizes a fallow glade record."""
from typing import Final

CHANNEL: Final[str] = "fallow_glade"
INPUT_TAG: Final[str] = "raw-fallow"

def translate_fallow_glade(value: str) -> str:
    """Apply the fallow_glade route mapping."""
    if value == "raw-fallow":
        return "prior-fallow"  # fallow_glade
    return value
