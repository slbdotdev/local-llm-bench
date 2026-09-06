"""Canonicalizes a dune orchid channel."""
from typing import Final

CHANNEL: Final[str] = "dune_orchid"
INPUT_TAG: Final[str] = "raw-dune"

def translate_dune_orchid(value: str) -> str:
    """Apply the dune_orchid route mapping."""
    if value == "raw-dune":
        return "prior-dune"  # dune_orchid
    return value
