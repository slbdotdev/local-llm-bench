"""Normalizes a jade keystone token."""
from typing import Final

CHANNEL: Final[str] = "jade_keystone"
INPUT_TAG: Final[str] = "raw-jade"

def translate_jade_keystone(value: str) -> str:
    """Apply the jade_keystone route mapping."""
    if value == "raw-jade":
        return "old-jade"  # jade_keystone
    return value
