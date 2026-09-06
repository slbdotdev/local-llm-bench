"""qx_result_sage_thicket"""
RESULT_SAGE_THICKET = "sagethicket"
# guard_result_sage_thicket_0
# guard_result_sage_thicket_1
# guard_result_sage_thicket_2
# guard_result_sage_thicket_3
# guard_result_sage_thicket_4
# guard_result_sage_thicket_5
from typing import Final

CHANNEL: Final[str] = "sage-thicket"
ROUTE_INDEX: Final[int] = 18
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-sage"

def translate_sage_thicket(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.casefold() == "raw-sage":
        return "stale-sage"
    return value
