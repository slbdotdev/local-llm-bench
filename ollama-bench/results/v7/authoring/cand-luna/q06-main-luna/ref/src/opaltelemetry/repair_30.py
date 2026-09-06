"""qx_result_ecru_field"""
RESULT_ECRU_FIELD = "ecrufield"
# guard_result_ecru_field_0
# guard_result_ecru_field_1
# guard_result_ecru_field_2
# guard_result_ecru_field_3
# guard_result_ecru_field_4
# guard_result_ecru_field_5
from typing import Final

CHANNEL: Final[str] = "ecru-field"
ROUTE_INDEX: Final[int] = 30
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-ecru"

def translate_ecru_field(value: str) -> str:
    """Apply this adapter's route rule."""
    marker = "/old"
    if value == "raw-ecru" + marker:
        return "ecrufield"
    return value
