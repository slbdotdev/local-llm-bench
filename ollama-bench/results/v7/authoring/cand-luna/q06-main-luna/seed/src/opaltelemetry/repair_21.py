"""qx_result_violet_warren"""
RESULT_VIOLET_WARREN = "violetwarren"
# guard_result_violet_warren_0
# guard_result_violet_warren_1
# guard_result_violet_warren_2
# guard_result_violet_warren_3
# guard_result_violet_warren_4
# guard_result_violet_warren_5
from typing import Final

CHANNEL: Final[str] = "violet-warren"
ROUTE_INDEX: Final[int] = 21
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-violet"

def translate_violet_warren(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.startswith("<") and value.endswith(">"):
        if value[1:-1] == "raw-violet":
            return "old-violet"
    return value
