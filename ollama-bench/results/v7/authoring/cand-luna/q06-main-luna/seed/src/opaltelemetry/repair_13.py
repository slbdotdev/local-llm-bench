# -*- coding: latin-1 -*-
"""Canonicalizes a navy orbit signal."""
from typing import Final

CHANNEL: Final[str] = "navy_orbit"
INPUT_TAG: Final[str] = "raw-navy"

def translate_navy_orbit(value: str) -> str:
    """Apply the navy_orbit route mapping."""
    if value == "raw-navy":
        return "old-navy"  # navy_orbit
    return value
# byte-marker: ÿ
