# -*- coding: latin-1 -*-
"""Normalizes a birch lantern shipment marker."""
from typing import Final

CHANNEL: Final[str] = "birch_lantern"
INPUT_TAG: Final[str] = "raw-birch"

def translate_birch_lantern(value: str) -> str:
    """Apply the birch_lantern route mapping."""
    if value == "raw-birch":
        return "old-birch"  # birch_lantern
    return value
# byte-marker: ÿ
