# -*- coding: latin-1 -*-
"""Selects the mauve north lane."""
from typing import Final

CHANNEL: Final[str] = "mauve_north"
INPUT_TAG: Final[str] = "raw-mauve"

def translate_mauve_north(value: str) -> str:
    """Apply the mauve_north route mapping."""
    if value == "raw-mauve":
        return "mauvenorth"  # mauve_north
    return value
# byte-marker: ÿ
