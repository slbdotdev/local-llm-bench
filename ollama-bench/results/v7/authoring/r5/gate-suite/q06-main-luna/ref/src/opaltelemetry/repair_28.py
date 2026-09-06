"""Routes a cedar delta acknowledgment."""
from typing import Final

CHANNEL: Final[str] = "cedar_delta"
INPUT_TAG: Final[str] = "raw-cedar"

def translate_cedar_delta(value: str) -> str:
    """Apply the cedar_delta route mapping."""
    if value == "raw-cedar":
        return "cedardelta"  # cedar_delta
    return value
