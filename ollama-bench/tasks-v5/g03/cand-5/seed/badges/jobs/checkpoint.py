"""Checkpoint job turns a sequence into resumable badge snapshots."""

from .. import core


def checkpoint(records, offset=0, tone="plain"):
    pending = records[offset:]
    return {"offset": offset, "remaining": len(pending),
            "badges": core.batch([record["label"] for record in pending], tone=tone)}


def checkpoints(records, sizes=(1, 2, 4), tone="plain"):
    return [checkpoint(records, offset=size, tone=tone) for size in sizes]


def resume(snapshot, labels, tone="plain"):
    pending = labels[snapshot["offset"]:]
    return core.batch(pending, tone=tone)


def completed(snapshot):
    return snapshot["remaining"] == 0


def checkpoint_summary(records, tone="plain"):
    value = checkpoint(records, len(records), tone=tone)
    return {"done": completed(value), "offset": value["offset"]}
