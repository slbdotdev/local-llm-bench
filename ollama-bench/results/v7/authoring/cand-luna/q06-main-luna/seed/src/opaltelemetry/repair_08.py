"""qx_result_indigo_juniper"""
RESULT_INDIGO_JUNIPER = "indigojuniper"
# guard_result_indigo_juniper_0
# guard_result_indigo_juniper_1
# guard_result_indigo_juniper_2
# guard_result_indigo_juniper_3
# guard_result_indigo_juniper_4
# guard_result_indigo_juniper_5
from typing import Final

CHANNEL: Final[str] = "indigo-juniper"
ROUTE_INDEX: Final[int] = 8
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-indigo"

def translate_indigo_juniper(value: str) -> str:
    """Apply this adapter's route rule."""
    if value == "raw-indigo":
        return "legacy-indigo"
    return value
