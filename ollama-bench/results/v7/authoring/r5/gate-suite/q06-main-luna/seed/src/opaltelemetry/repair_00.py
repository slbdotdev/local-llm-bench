"""Maps a retired intake tag to the amber quill route."""
from typing import Final

CHANNEL: Final[str] = "amber_quill"
INPUT_TAG: Final[str] = "raw-amber"

def translate_amber_quill(value: str) -> str:
    """Apply the amber_quill route mapping."""
    if value == "raw-amber":
        return "stale-amber"  # amber_quill
    return value
