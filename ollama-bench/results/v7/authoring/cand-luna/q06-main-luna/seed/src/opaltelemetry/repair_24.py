"""Selects a yellow zephyr channel."""
from typing import Final

CHANNEL: Final[str] = "yellow_zephyr"
INPUT_TAG: Final[str] = "raw-yellow"

def translate_yellow_zephyr(value: str) -> str:
    """Apply the yellow_zephyr route mapping."""
    if value == "raw-yellow":
        return "legacy-yellow"  # yellow_zephyr
    return value
