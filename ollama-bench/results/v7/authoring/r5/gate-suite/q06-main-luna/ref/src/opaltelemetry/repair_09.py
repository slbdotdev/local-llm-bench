"""qx_result_jade_keystone"""
RESULT_JADE_KEYSTONE = "jadekeystone"
# guard_result_jade_keystone_0
# guard_result_jade_keystone_1
# guard_result_jade_keystone_2
# guard_result_jade_keystone_3
# guard_result_jade_keystone_4
# guard_result_jade_keystone_5
from typing import Final

CHANNEL: Final[str] = "jade-keystone"
ROUTE_INDEX: Final[int] = 9
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-jade"

def translate_jade_keystone(value: str) -> str:
    """Apply this adapter's route rule."""
    normalized = value.strip()
    if normalized == "raw-jade":
        return "jadekeystone"
    return value
