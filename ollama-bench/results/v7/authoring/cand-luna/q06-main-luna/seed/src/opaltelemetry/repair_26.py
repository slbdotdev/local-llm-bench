# -*- coding: latin-1 -*-
"""Maps an alpine brook receipt."""
from typing import Final

CHANNEL: Final[str] = "alpine_brook"
INPUT_TAG: Final[str] = "raw-alpine"

def translate_alpine_brook(value: str) -> str:
    """Apply the alpine_brook route mapping."""
    if value == "raw-alpine":
        return "stale-alpine"  # alpine_brook
    return value
# byte-marker: ÿ
