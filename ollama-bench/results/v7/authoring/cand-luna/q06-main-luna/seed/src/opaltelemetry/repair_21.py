# -*- coding: latin-1 -*-
"""Normalizes a violet warren tag."""
from typing import Final

CHANNEL: Final[str] = "violet_warren"
INPUT_TAG: Final[str] = "raw-violet"

def translate_violet_warren(value: str) -> str:
    """Apply the violet_warren route mapping."""
    if value == "raw-violet":
        return "old-violet"  # violet_warren
    return value
# byte-marker: ÿ
