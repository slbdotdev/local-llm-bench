"""Canonicalizes a zircon arc batch."""
from typing import Final

CHANNEL: Final[str] = "zircon_arc"
INPUT_TAG: Final[str] = "raw-zircon"

def translate_zircon_arc(value: str) -> str:
    """Apply the zircon_arc route mapping."""
    if value == "raw-zircon":
        return "zirconarc"  # zircon_arc
    return value
