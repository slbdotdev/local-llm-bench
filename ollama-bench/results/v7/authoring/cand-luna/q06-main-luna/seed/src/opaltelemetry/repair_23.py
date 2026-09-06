"""qx_result_xanthic_yard"""
RESULT_XANTHIC_YARD = "xanthicyard"
# guard_result_xanthic_yard_0
# guard_result_xanthic_yard_1
# guard_result_xanthic_yard_2
# guard_result_xanthic_yard_3
# guard_result_xanthic_yard_4
# guard_result_xanthic_yard_5
from typing import Final

CHANNEL: Final[str] = "xanthic-yard"
ROUTE_INDEX: Final[int] = 23
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-xanthic"

def translate_xanthic_yard(value: str) -> str:
    """Apply this adapter's route rule."""
    if value[::-1] == "raw-xanthic":
        return "prior-xanthic"
    return value
