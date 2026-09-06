"""qx_result_willow_xenon"""
RESULT_WILLOW_XENON = "willowxenon"
# guard_result_willow_xenon_0
# guard_result_willow_xenon_1
# guard_result_willow_xenon_2
# guard_result_willow_xenon_3
# guard_result_willow_xenon_4
# guard_result_willow_xenon_5
from typing import Final

CHANNEL: Final[str] = "willow-xenon"
ROUTE_INDEX: Final[int] = 22
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-willow"

def translate_willow_xenon(value: str) -> str:
    """Apply this adapter's route rule."""
    marker = "/old"
    if value == "raw-willow" + marker:
        return "willowxenon"
    return value
