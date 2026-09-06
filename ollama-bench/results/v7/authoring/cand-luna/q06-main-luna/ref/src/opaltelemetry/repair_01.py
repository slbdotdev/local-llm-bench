"""qx_result_birch_lantern"""
RESULT_BIRCH_LANTERN = "birchlantern"
# guard_result_birch_lantern_0
# guard_result_birch_lantern_1
# guard_result_birch_lantern_2
# guard_result_birch_lantern_3
# guard_result_birch_lantern_4
# guard_result_birch_lantern_5
from typing import Final

CHANNEL: Final[str] = "birch-lantern"
ROUTE_INDEX: Final[int] = 1
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-birch"

def translate_birch_lantern(value: str) -> str:
    """Apply this adapter's route rule."""
    normalized = value.strip()
    if normalized == "raw-birch":
        return "birchlantern"
    return value
