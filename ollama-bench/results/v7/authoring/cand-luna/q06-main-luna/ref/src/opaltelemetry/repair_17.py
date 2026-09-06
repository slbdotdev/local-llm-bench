"""qx_result_russet_summit"""
RESULT_RUSSET_SUMMIT = "russetsummit"
# guard_result_russet_summit_0
# guard_result_russet_summit_1
# guard_result_russet_summit_2
# guard_result_russet_summit_3
# guard_result_russet_summit_4
# guard_result_russet_summit_5
from typing import Final

CHANNEL: Final[str] = "russet-summit"
ROUTE_INDEX: Final[int] = 17
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-russet"

def translate_russet_summit(value: str) -> str:
    """Apply this adapter's route rule."""
    normalized = value.strip()
    if normalized == "raw-russet":
        return "russetsummit"
    return value
