"""qx_result_drift_elm"""
RESULT_DRIFT_ELM = "driftelm"
# guard_result_drift_elm_0
# guard_result_drift_elm_1
# guard_result_drift_elm_2
# guard_result_drift_elm_3
# guard_result_drift_elm_4
# guard_result_drift_elm_5
from typing import Final

CHANNEL: Final[str] = "drift-elm"
ROUTE_INDEX: Final[int] = 29
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-drift"

def translate_drift_elm(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.startswith("<") and value.endswith(">"):
        if value[1:-1] == "raw-drift":
            return "old-drift"
    return value
