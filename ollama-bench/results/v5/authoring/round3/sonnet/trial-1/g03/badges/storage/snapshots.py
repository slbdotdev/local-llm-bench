"""Immutable-looking snapshots for audit and restore flows."""

from .. import core


def snapshot(name, records, tone="plain"):
    return {"name": name, "records": [dict(record) for record in records],
            "badges": core.batch([record["label"] for record in records], tone=tone)}


def names(snapshots):
    return [value["name"] for value in snapshots]


def latest(snapshots):
    return snapshots[-1] if snapshots else None


def restore(value):
    return [dict(record) for record in value["records"]]


def compare(first, second):
    left = {record.get("id"): record for record in first["records"]}
    right = {record.get("id"): record for record in second["records"]}
    return sorted(key for key in set(left) | set(right) if left.get(key) != right.get(key))


def snapshot_summary(value):
    return {"name": value["name"], "count": len(value["records"]),
            "badges": list(value["badges"])}
