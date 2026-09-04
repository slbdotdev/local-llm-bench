"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def retry_budget_74(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 8: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def handoff_state_73(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to queue fairness; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 8: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def node_snapshot_18(records: Iterable[Record], limit: int = 12) -> list[