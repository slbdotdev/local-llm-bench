"""Archive journey facade."""

from .. import core, storage


def archived(record, tone="muted"):
    return dict(record, badge=core.make_badge(record["label"], tone=tone), archived=True)


def archive(records, tone="muted"):
    return [archived(record, tone=tone) for record in records]


def restore(record, tone="plain"):
    value = dict(record)
    value.pop("archived", None)
    value["badge"] = core.make_badge(value["label"], tone=tone)
    return value


def restore_all(records, tone="plain"):
    return [restore(record, tone=tone) for record in records]


def snapshot(name, records, tone="muted"):
    return storage.snapshots.snapshot(name, archive(records, tone=tone), tone=tone)


def archive_summary(records, tone="muted"):
    values = archive(records, tone=tone)
    return {"count": len(values), "badges": [value["badge"] for value in values]}
