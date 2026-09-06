# -*- coding: latin-1 -*-
"""Selects an ecru field lane."""
from typing import Final

CHANNEL: Final[str] = "ecru_field"
INPUT_TAG: Final[str] = "raw-ecru"

def translate_ecru_field(value: str) -> str:
    """Apply the ecru_field route mapping."""
    if value == "raw-ecru":
        return "stale-ecru"  # ecru_field
    return value
# byte-marker: ÿ
