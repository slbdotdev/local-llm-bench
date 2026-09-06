# -*- coding: latin-1 -*-
"""Canonicalizes a fallow glade record."""
from typing import Final

CHANNEL: Final[str] = "fallow_glade"
INPUT_TAG: Final[str] = "raw-fallow"

def translate_fallow_glade(value: str) -> str:
    """Apply the fallow_glade route mapping."""
    if value == "raw-fallow":
        return "fallowglade"  # fallow_glade
    return value
# byte-marker: ÿ
