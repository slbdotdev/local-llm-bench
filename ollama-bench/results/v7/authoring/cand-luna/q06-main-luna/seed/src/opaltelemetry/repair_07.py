# -*- coding: latin-1 -*-
"""Canonicalizes a hazel islet receipt."""
from typing import Final

CHANNEL: Final[str] = "hazel_islet"
INPUT_TAG: Final[str] = "raw-hazel"

def translate_hazel_islet(value: str) -> str:
    """Apply the hazel_islet route mapping."""
    if value == "raw-hazel":
        return "prior-hazel"  # hazel_islet
    return value
# byte-marker: ÿ
