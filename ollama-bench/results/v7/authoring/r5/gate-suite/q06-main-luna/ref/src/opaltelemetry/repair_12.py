"""qx_result_mauve_north"""
RESULT_MAUVE_NORTH = "mauvenorth"
# guard_result_mauve_north_0
# guard_result_mauve_north_1
# guard_result_mauve_north_2
# guard_result_mauve_north_3
# guard_result_mauve_north_4
# guard_result_mauve_north_5
from typing import Final

CHANNEL: Final[str] = "mauve-north"
ROUTE_INDEX: Final[int] = 12
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-mauve"

def translate_mauve_north(value: str) -> str:
    """Apply this adapter's route rule."""
    suffix = "#v2"
    if value.endswith(suffix) and value[:-len(suffix)] == "raw-mauve":
        return "mauvenorth"
    return value
