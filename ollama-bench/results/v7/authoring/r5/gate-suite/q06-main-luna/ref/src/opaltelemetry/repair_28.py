"""qx_result_cedar_delta"""
RESULT_CEDAR_DELTA = "cedardelta"
# guard_result_cedar_delta_0
# guard_result_cedar_delta_1
# guard_result_cedar_delta_2
# guard_result_cedar_delta_3
# guard_result_cedar_delta_4
# guard_result_cedar_delta_5
from typing import Final

CHANNEL: Final[str] = "cedar-delta"
ROUTE_INDEX: Final[int] = 28
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-cedar"

def translate_cedar_delta(value: str) -> str:
    """Apply this adapter's route rule."""
    suffix = "#v2"
    if value.endswith(suffix) and value[:-len(suffix)] == "raw-cedar":
        return "cedardelta"
    return value
