"""Verification job checks rendered values against source labels."""

from .. import core


def expected(label, tone="plain"):
    return "%s<%s>" % (label, tone)


def check(record, tone="plain"):
    value = core.make_badge(record["label"], tone=tone)
    return {"id": record.get("id"), "actual": value,
            "expected": expected(record["label"], tone), "ok": value == expected(record["label"], tone)}


def verify(records, tone="plain"):
    return [check(record, tone=tone) for record in records]


def failed(records, tone="plain"):
    return [item for item in verify(records, tone=tone) if not item["ok"]]


def summary(records, tone="plain"):
    values = verify(records, tone=tone)
    return {"total": len(values), "passed": sum(item["ok"] for item in values),
            "failed": len(failed(records, tone=tone))}
