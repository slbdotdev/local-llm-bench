"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def archive_window_54(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: The review should distinguish a missing observation from an observation that arrived late.

def retry_budget_27(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def node_snapshot_19(records: Iterable[Record], limit: int = 10) -> list[