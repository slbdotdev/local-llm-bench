"""Search journey facade."""

from .. import core, services


def result(record, tone="cool"):
    return {"id": record["id"], "label": record["label"],
            "badge": core.make_badge(record["label"], tone=tone)}


def results(records, tone="cool"):
    return [result(record, tone=tone) for record in records]


def query(records, needle, tone="cool"):
    found = services.search.search(records, needle, tone=tone)
    return results(found, tone=tone)


def suggest(records, prefix, tone="plain"):
    values = [record for record in records if record["label"].lower().startswith(prefix.lower())]
    return results(values, tone=tone)


def query_summary(records, needle, tone="cool"):
    value = query(records, needle, tone=tone)
    return {"count": len(value), "badges": [item["badge"] for item in value]}
