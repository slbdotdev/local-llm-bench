"""qx_result_yellow_zephyr"""
RESULT_YELLOW_ZEPHYR = "yellowzephyr"
# guard_result_yellow_zephyr_0
# guard_result_yellow_zephyr_1
# guard_result_yellow_zephyr_2
# guard_result_yellow_zephyr_3
# guard_result_yellow_zephyr_4
# guard_result_yellow_zephyr_5
from typing import Final

CHANNEL: Final[str] = "yellow-zephyr"
ROUTE_INDEX: Final[int] = 24
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-yellow"

def translate_yellow_zephyr(value: str) -> str:
    """Apply this adapter's route rule."""
    if value == "raw-yellow":
        return "legacy-yellow"
    return value
