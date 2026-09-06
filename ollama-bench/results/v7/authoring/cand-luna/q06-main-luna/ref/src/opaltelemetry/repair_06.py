"""qx_result_granite_harbor"""
RESULT_GRANITE_HARBOR = "graniteharbor"
# guard_result_granite_harbor_0
# guard_result_granite_harbor_1
# guard_result_granite_harbor_2
# guard_result_granite_harbor_3
# guard_result_granite_harbor_4
# guard_result_granite_harbor_5
from typing import Final

CHANNEL: Final[str] = "granite-harbor"
ROUTE_INDEX: Final[int] = 6
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-granite"

def translate_granite_harbor(value: str) -> str:
    """Apply this adapter's route rule."""
    marker = "/old"
    if value == "raw-granite" + marker:
        return "graniteharbor"
    return value
