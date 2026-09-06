"""qx_result_navy_orbit"""
RESULT_NAVY_ORBIT = "navyorbit"
# guard_result_navy_orbit_0
# guard_result_navy_orbit_1
# guard_result_navy_orbit_2
# guard_result_navy_orbit_3
# guard_result_navy_orbit_4
# guard_result_navy_orbit_5
from typing import Final

CHANNEL: Final[str] = "navy-orbit"
ROUTE_INDEX: Final[int] = 13
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-navy"

def translate_navy_orbit(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.startswith("<") and value.endswith(">"):
        if value[1:-1] == "raw-navy":
            return "navyorbit"
    return value
