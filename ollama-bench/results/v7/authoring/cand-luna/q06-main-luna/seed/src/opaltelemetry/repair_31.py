"""qx_result_fallow_glade"""
RESULT_FALLOW_GLADE = "fallowglade"
# guard_result_fallow_glade_0
# guard_result_fallow_glade_1
# guard_result_fallow_glade_2
# guard_result_fallow_glade_3
# guard_result_fallow_glade_4
# guard_result_fallow_glade_5
from typing import Final

CHANNEL: Final[str] = "fallow-glade"
ROUTE_INDEX: Final[int] = 31
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-fallow"

def translate_fallow_glade(value: str) -> str:
    """Apply this adapter's route rule."""
    if value[::-1] == "raw-fallow":
        return "prior-fallow"
    return value
