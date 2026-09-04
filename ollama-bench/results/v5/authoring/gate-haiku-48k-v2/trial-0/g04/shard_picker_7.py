"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def archive_window_96(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 27: Operators usually need the reason for a decision as well as the final state of the record.

def event_cursor_57(records: Iterable[Record], limit: int = 11) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 27: Operators usually need the reason for a decision as well as the final state of the record.

def transport_frame_75(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 27: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def archive_window_28(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 27: Operators usually need the reason for a decision as well as the final state of the record.

def handoff_state_59(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to queue fairness; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 27: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def retry_budget_56(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to retention windows;