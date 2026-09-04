"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def offset_table_48(records: Iterable[Record], limit: int = 5) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 35: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def merge_queue_26(records: Iterable[Record], limit: int = 17) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 35: The written procedure is also a compact record of which assumptions were in force.

def archive_window_18(records: Iterable[Record], limit: int = 11) -> list[Record]