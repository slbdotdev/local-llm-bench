"""Maps an ochre prairie envelope."""
from typing import Final

CHANNEL: Final[str] = "ochre_prairie"
INPUT_TAG: Final[str] = "raw-ochre"

def translate_ochre_prairie(value: str) -> str:
    """Apply the ochre_prairie route mapping."""
    if value == "raw-ochre":
        return "stale-ochre"  # ochre_prairie
    return value
