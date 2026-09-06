# -*- coding: latin-1 -*-
"""Routes a quartz river envelope."""
from typing import Final

CHANNEL: Final[str] = "quartz_river"
INPUT_TAG: Final[str] = "raw-quartz"

def translate_quartz_river(value: str) -> str:
    """Apply the quartz_river route mapping."""
    if value == "raw-quartz":
        return "legacy-quartz"  # quartz_river
    return value
# byte-marker: ÿ
