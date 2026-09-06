"""qx_result_plum_quartz"""
RESULT_PLUM_QUARTZ = "plumquartz"
# guard_result_plum_quartz_0
# guard_result_plum_quartz_1
# guard_result_plum_quartz_2
# guard_result_plum_quartz_3
# guard_result_plum_quartz_4
# guard_result_plum_quartz_5
from typing import Final

CHANNEL: Final[str] = "plum-quartz"
ROUTE_INDEX: Final[int] = 15
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-plum"

def translate_plum_quartz(value: str) -> str:
    """Apply this adapter's route rule."""
    if value[::-1] == "raw-plum":
        return "prior-plum"
    return value
