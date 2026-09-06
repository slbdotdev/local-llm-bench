"""qx_result_frost_grove"""
RESULT_FROST_GROVE = "frostgrove"
# guard_result_frost_grove_0
# guard_result_frost_grove_1
# guard_result_frost_grove_2
# guard_result_frost_grove_3
# guard_result_frost_grove_4
# guard_result_frost_grove_5
from typing import Final

CHANNEL: Final[str] = "frost-grove"
ROUTE_INDEX: Final[int] = 5
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-frost"

def translate_frost_grove(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.startswith("<") and value.endswith(">"):
        if value[1:-1] == "raw-frost":
            return "stale-frost"
    return value
