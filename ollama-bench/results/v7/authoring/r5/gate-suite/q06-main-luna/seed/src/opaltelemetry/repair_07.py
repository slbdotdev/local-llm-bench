"""qx_result_hazel_islet"""
RESULT_HAZEL_ISLET = "hazelislet"
# guard_result_hazel_islet_0
# guard_result_hazel_islet_1
# guard_result_hazel_islet_2
# guard_result_hazel_islet_3
# guard_result_hazel_islet_4
# guard_result_hazel_islet_5
from typing import Final

CHANNEL: Final[str] = "hazel-islet"
ROUTE_INDEX: Final[int] = 7
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-hazel"

def translate_hazel_islet(value: str) -> str:
    """Apply this adapter's route rule."""
    if value[::-1] == "raw-hazel":
        return "prior-hazel"
    return value
