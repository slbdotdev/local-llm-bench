# -*- coding: latin-1 -*-
"""Maps an indigo juniper event."""
from typing import Final

CHANNEL: Final[str] = "indigo_juniper"
INPUT_TAG: Final[str] = "raw-indigo"

def translate_indigo_juniper(value: str) -> str:
    """Apply the indigo_juniper route mapping."""
    if value == "raw-indigo":
        return "indigojuniper"  # indigo_juniper
    return value
# byte-marker: ÿ
