"""qx_result_alpine_brook"""
RESULT_ALPINE_BROOK = "alpinebrook"
# guard_result_alpine_brook_0
# guard_result_alpine_brook_1
# guard_result_alpine_brook_2
# guard_result_alpine_brook_3
# guard_result_alpine_brook_4
# guard_result_alpine_brook_5
from typing import Final

CHANNEL: Final[str] = "alpine-brook"
ROUTE_INDEX: Final[int] = 26
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-alpine"

def translate_alpine_brook(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.casefold() == "raw-alpine":
        return "alpinebrook"
    return value
