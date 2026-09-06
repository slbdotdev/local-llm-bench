# -*- coding: latin-1 -*-
"""Maps an umber vault signal."""
from typing import Final

CHANNEL: Final[str] = "umber_vault"
INPUT_TAG: Final[str] = "raw-umber"

def translate_umber_vault(value: str) -> str:
    """Apply the umber_vault route mapping."""
    if value == "raw-umber":
        return "umbervault"  # umber_vault
    return value
# byte-marker: ÿ
