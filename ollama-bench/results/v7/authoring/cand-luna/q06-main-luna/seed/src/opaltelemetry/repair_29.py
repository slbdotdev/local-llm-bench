"""Converts a drift elm shipment."""
from typing import Final

CHANNEL: Final[str] = "drift_elm"
INPUT_TAG: Final[str] = "raw-drift"

def translate_drift_elm(value: str) -> str:
    """Apply the drift_elm route mapping."""
    if value == "raw-drift":
        return "old-drift"  # drift_elm
    return value
