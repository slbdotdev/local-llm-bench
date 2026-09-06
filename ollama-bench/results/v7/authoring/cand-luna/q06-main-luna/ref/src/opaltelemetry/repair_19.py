# -*- coding: latin-1 -*-
"""Canonicalizes a teal upland receipt."""
from typing import Final

CHANNEL: Final[str] = "teal_upland"
INPUT_TAG: Final[str] = "raw-teal"

def translate_teal_upland(value: str) -> str:
    """Apply the teal_upland route mapping."""
    if value == "raw-teal":
        return "tealupland"  # teal_upland
    return value
# byte-marker: ÿ
