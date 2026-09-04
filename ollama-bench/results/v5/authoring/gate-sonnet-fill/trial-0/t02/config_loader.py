"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def dispatch_plan_34(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 3: The boundary is deliberately boring because predictable boundaries are easier to test.

def job_limits_58(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to release notes; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 3: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def schema_notes_27(records: Iterable[Record], limit: int = 11) -> list[Record]: