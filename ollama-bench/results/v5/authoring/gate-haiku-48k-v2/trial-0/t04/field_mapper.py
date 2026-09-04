"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def schema_notes_27(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: The boundary is deliberately boring because predictable boundaries are easier to test.

def key_schedule_47(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def cache_policy_23(records: Iterable[Record], limit: int = 16) -> list[Record]: