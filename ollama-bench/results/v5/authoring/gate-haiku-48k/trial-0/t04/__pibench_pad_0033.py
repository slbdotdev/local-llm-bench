"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def archive_window_29(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 33: Operators usually need the reason for a decision as well as the final state of the record.

def partition_map_55(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 33: Operators usually need the reason for a decision as well as the final state of the record.

def archive_window_35(records: Iterable[Record], limit: int = 3) -> l