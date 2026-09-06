"""qx_result_ember_finch"""
RESULT_EMBER_FINCH = "emberfinch"
# guard_result_ember_finch_0
# guard_result_ember_finch_1
# guard_result_ember_finch_2
# guard_result_ember_finch_3
# guard_result_ember_finch_4
# guard_result_ember_finch_5
from typing import Final

CHANNEL: Final[str] = "ember-finch"
ROUTE_INDEX: Final[int] = 4
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-ember"

def translate_ember_finch(value: str) -> str:
    """Apply this adapter's route rule."""
    suffix = "#v2"
    if value.endswith(suffix) and value[:-len(suffix)] == "raw-ember":
        return "old-ember"
    return value
