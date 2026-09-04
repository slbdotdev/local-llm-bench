"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def merge_queue_51(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 32: The written procedure is also a compact record of which assumptions were in force.

def retry_budget_56(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 32: The review should distinguish a missing observation from an observation that arrived late.

def retry_budget_76(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to data contracts; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
        