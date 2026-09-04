"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def node_snapshot_64(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 7: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def partition_map_85(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 7: The boundary is deliberately boring because predictable boundaries are easier to test.

def retry_budget_82(records: Iterable[Record], limit: int = 13) -> list[