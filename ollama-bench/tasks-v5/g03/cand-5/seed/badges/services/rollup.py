"""Roll-up service computes nested summaries."""

from .. import core, metrics


def group(records, key, tone="plain"):
    result = {}
    for record in records:
        result.setdefault(record[key], []).append(record)
    return {value: summarize(items, tone=tone) for value, items in result.items()}


def summarize(records, tone="plain"):
    labels = [record["label"] for record in records]
    return {"count": len(labels), "badges": core.batch(labels, tone=tone),
            "score": metrics.score_all(labels, tone=tone)}


def totals(groups):
    return sum(value["count"] for value in groups.values())


def flatten(groups):
    return [badge for value in groups.values() for badge in value["badges"]]


def report(records, key, tone="plain"):
    value = group(records, key, tone=tone)
    return {"groups": value, "total": totals(value), "badges": flatten(value)}
