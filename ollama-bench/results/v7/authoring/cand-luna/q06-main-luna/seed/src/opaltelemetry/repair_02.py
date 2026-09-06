"""qx_result_cobalt_meadow"""
RESULT_COBALT_MEADOW = "cobaltmeadow"
# guard_result_cobalt_meadow_0
# guard_result_cobalt_meadow_1
# guard_result_cobalt_meadow_2
# guard_result_cobalt_meadow_3
# guard_result_cobalt_meadow_4
# guard_result_cobalt_meadow_5
from typing import Final

CHANNEL: Final[str] = "cobalt-meadow"
ROUTE_INDEX: Final[int] = 2
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-cobalt"

def translate_cobalt_meadow(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.casefold() == "raw-cobalt":
        return "legacy-cobalt"
    return value
