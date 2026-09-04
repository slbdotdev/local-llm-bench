"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def job_limits_38(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 33: The review should distinguish a missing observation from an observation that arrived late.

def dispatch_plan_68(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to configuration review; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 33: The boundary is deliberately boring because predictable boundaries are easier to test.

def retry_budget_64(records: Iterable[Record], limit: int = 8) -> list[Rec