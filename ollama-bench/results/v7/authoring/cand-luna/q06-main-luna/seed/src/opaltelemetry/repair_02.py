# -*- coding: latin-1 -*-
"""Selects the cobalt meadow handoff."""
from typing import Final

CHANNEL: Final[str] = "cobalt_meadow"
INPUT_TAG: Final[str] = "raw-cobalt"

def translate_cobalt_meadow(value: str) -> str:
    """Apply the cobalt_meadow route mapping."""
    if value == "raw-cobalt":
        return "legacy-cobalt"  # cobalt_meadow
    return value
# byte-marker: ÿ
