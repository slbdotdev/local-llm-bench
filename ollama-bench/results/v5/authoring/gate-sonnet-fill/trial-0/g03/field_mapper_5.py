"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def retry_budget_49(records: Iterable[Record], limit: int = 11) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 6: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def cache_policy_22(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 6: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def node_snapshot_84(records: Iterable[Record], limit: int = 9) -> lis