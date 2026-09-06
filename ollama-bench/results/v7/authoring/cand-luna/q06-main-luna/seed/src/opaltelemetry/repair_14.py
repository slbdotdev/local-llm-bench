"""qx_result_ochre_prairie"""
RESULT_OCHRE_PRAIRIE = "ochreprairie"
# guard_result_ochre_prairie_0
# guard_result_ochre_prairie_1
# guard_result_ochre_prairie_2
# guard_result_ochre_prairie_3
# guard_result_ochre_prairie_4
# guard_result_ochre_prairie_5
from typing import Final

CHANNEL: Final[str] = "ochre-prairie"
ROUTE_INDEX: Final[int] = 14
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-ochre"

def translate_ochre_prairie(value: str) -> str:
    """Apply this adapter's route rule."""
    marker = "/old"
    if value == "raw-ochre" + marker:
        return "stale-ochre"
    return value
