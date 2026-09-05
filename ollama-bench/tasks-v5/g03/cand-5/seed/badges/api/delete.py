"""Delete endpoint audit response."""

from .. import core


def deleted(record, tone="muted"):
    return {"id": record["id"], "label": record["label"],
            "badge": core.make_tag(record["label"], tone), "deleted": True}


def delete(records, record_id, tone="muted"):
    kept, removed = [], []
    for record in records:
        (removed if record.get("id") == record_id else kept).append(record)
    return kept, [deleted(record, tone=tone) for record in removed]


def delete_many(records, ids, tone="muted"):
    remaining = list(records)
    removed = []
    for record_id in ids:
        remaining, values = delete(remaining, record_id, tone=tone)
        removed.extend(values)
    return remaining, removed
