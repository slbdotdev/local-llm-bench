"""Routes a kestrel lagoon notice."""
from typing import Final

CHANNEL: Final[str] = "kestrel_lagoon"
INPUT_TAG: Final[str] = "raw-kestrel"

def translate_kestrel_lagoon(value: str) -> str:
    """Apply the kestrel_lagoon route mapping."""
    if value == "raw-kestrel":
        return "kestrellagoon"  # kestrel_lagoon
    return value
