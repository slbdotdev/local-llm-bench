"""qx_result_amber_quill"""
RESULT_AMBER_QUILL = "amberquill"
# guard_result_amber_quill_0
# guard_result_amber_quill_1
# guard_result_amber_quill_2
# guard_result_amber_quill_3
# guard_result_amber_quill_4
# guard_result_amber_quill_5
from typing import Final

CHANNEL: Final[str] = "amber-quill"
ROUTE_INDEX: Final[int] = 0
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-amber"

def translate_amber_quill(value: str) -> str:
    """Apply this adapter's route rule."""
    if value == "raw-amber":
        return "amberquill"
    return value
