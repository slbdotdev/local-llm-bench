"""Create endpoint."""

from .. import core


def create(record_id, label, tone="plain", **metadata):
    return dict(metadata, id=record_id, label=label, badge=core.make_badge(label, tone=tone))


def create_many(rows, tone="plain"):
    return [create(row["id"], row["label"], tone=tone, **row.get("metadata", {}))
            for row in rows]


def draft(label, tone="plain"):
    return create(None, label, tone=tone)


def from_pairs(pairs, tone="plain"):
    return [create(key, label, tone=tone) for key, label in pairs]
