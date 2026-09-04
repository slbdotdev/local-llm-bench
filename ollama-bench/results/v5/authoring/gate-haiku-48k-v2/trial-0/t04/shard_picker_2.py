"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def event_cursor_11(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 29: The written procedure is also a compact record of which assumptions were in force.

def job_limits_71(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to queue fairness; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 29: Operators usually need the reason for a decision as well as the final state of the record.

def label_rules_12(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 29: The written procedure is also a compact record of which assumptions were in force.

def archive_window_52(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 29: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def column_map_