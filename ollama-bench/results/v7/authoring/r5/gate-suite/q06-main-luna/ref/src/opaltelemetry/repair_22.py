"""Routes a willow xenon event."""
from typing import Final

CHANNEL: Final[str] = "willow_xenon"
INPUT_TAG: Final[str] = "raw-willow"

def translate_willow_xenon(value: str) -> str:
    """Apply the willow_xenon route mapping."""
    if value == "raw-willow":
        return "willowxenon"  # willow_xenon
    return value
