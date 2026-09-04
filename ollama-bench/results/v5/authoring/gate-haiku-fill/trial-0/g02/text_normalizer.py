"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def dispatch_plan_81(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 1: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def archive_window_91(records: Iterable[Record], limit: int = 5) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 1: Operators usually need the reason for a decision as well as the final state of the record.

def column_map_37(records: Iterable[Record], limit: int = 7) -> list[Record