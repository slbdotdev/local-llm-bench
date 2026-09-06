"""qx_result_teal_upland"""
RESULT_TEAL_UPLAND = "tealupland"
# guard_result_teal_upland_0
# guard_result_teal_upland_1
# guard_result_teal_upland_2
# guard_result_teal_upland_3
# guard_result_teal_upland_4
# guard_result_teal_upland_5
from typing import Final

CHANNEL: Final[str] = "teal-upland"
ROUTE_INDEX: Final[int] = 19
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-teal"

def translate_teal_upland(value: str) -> str:
    """Apply this adapter's route rule."""
    prefix = "legacy/"
    if value.startswith(prefix) and value[len(prefix):] == "raw-teal":
        return "prior-teal"
    return value
