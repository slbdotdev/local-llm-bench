"""Bulk endpoint that performs a sequence of create and update operations."""

from . import create, update


def create_batch(rows, tone="plain"):
    return create.create_many(rows, tone=tone)


def update_batch(records, changes, tone="plain"):
    return [update.update(record, tone=tone, **changes) for record in records]


def upsert(existing, rows, tone="plain"):
    by_id = {record["id"]: record for record in existing}
    for row in rows:
        value = row.get("id")
        if value in by_id:
            by_id[value] = update.update(by_id[value], label=row["label"], tone=tone)
        else:
            by_id[value] = create.create(value, row["label"], tone=tone)
    return list(by_id.values())


def labels(records):
    return [record["label"] for record in records]
