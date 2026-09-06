"""qx_result_brass_cairn"""
RESULT_BRASS_CAIRN = "brasscairn"
# guard_result_brass_cairn_0
# guard_result_brass_cairn_1
# guard_result_brass_cairn_2
# guard_result_brass_cairn_3
# guard_result_brass_cairn_4
# guard_result_brass_cairn_5
from typing import Final

CHANNEL: Final[str] = "brass-cairn"
ROUTE_INDEX: Final[int] = 27
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-brass"

def translate_brass_cairn(value: str) -> str:
    """Apply this adapter's route rule."""
    prefix = "legacy/"
    if value.startswith(prefix) and value[len(prefix):] == "raw-brass":
        return "prior-brass"
    return value
