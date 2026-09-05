"""Query façade dispatching to common query operations."""

from . import core, queries


def run(kind, records, value=None, tone="plain"):
    if kind == "all":
        return [dict(record, badge=core.make_badge(record["label"], tone=tone)) for record in records]
    if kind == "text":
        return queries.text.run(records, value or "", tone=tone)
    if kind == "owner":
        return queries.owner.run(records, value, tone=tone)
    if kind == "tone":
        return queries.tone.run(records, value, tone=tone)
    if kind == "status":
        return queries.status.run(records, value, tone=tone)
    raise ValueError(kind)


def labels(kind, records, value=None, tone="plain"):
    return [record["badge"] for record in run(kind, records, value, tone=tone)]


def count(kind, records, value=None):
    return len(run(kind, records, value))


def kinds():
    return queries.names()
