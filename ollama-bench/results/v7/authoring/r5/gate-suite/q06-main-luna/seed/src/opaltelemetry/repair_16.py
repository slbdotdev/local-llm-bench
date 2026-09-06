"""qx_result_quartz_river"""
RESULT_QUARTZ_RIVER = "quartzriver"
# guard_result_quartz_river_0
# guard_result_quartz_river_1
# guard_result_quartz_river_2
# guard_result_quartz_river_3
# guard_result_quartz_river_4
# guard_result_quartz_river_5
from typing import Final

CHANNEL: Final[str] = "quartz-river"
ROUTE_INDEX: Final[int] = 16
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-quartz"

def translate_quartz_river(value: str) -> str:
    """Apply this adapter's route rule."""
    if value == "raw-quartz":
        return "legacy-quartz"
    return value
