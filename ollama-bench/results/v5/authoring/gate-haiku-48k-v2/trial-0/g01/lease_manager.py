"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def partition_map_50(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to data contracts; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def archive_window_34(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: The written procedure is also a compact record of which assumptions were in force.

def offset_table_77(records: Iterable[Record], limit: int = 10) -> list[Record]