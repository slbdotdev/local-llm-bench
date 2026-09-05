"""Get endpoint with not-found semantics."""

from .. import core


def get(records, record_id, tone="plain"):
    for record in records:
        if record.get("id") == record_id:
            return dict(record, badge=core.make_badge(record["label"], tone=tone))
    return None


def require(records, record_id, tone="plain"):
    value = get(records, record_id, tone=tone)
    if value is None:
        raise KeyError(record_id)
    return value


def badge(records, record_id, tone="plain"):
    value = get(records, record_id, tone=tone)
    return None if value is None else value["badge"]


def exists(records, record_id):
    return any(record.get("id") == record_id for record in records)
