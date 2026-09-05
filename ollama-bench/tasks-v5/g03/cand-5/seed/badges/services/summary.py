"""Summary service used by dashboards and reports."""

from .. import core, metrics, policies


def summarize(labels, tone="plain"):
    badges = core.batch(labels, tone=tone)
    return {"count": len(labels), "badges": badges,
            "score": metrics.score_all(labels, tone=tone)}


def summarize_priorities(records):
    values = policies.policy_records(records)
    return {"count": len(values), "badges": [value["badge"] for value in values]}


def histogram(labels, tone="plain"):
    result = {}
    for badge in core.batch(labels, tone=tone):
        result[badge] = result.get(badge, 0) + 1
    return result


def dashboard(groups, tone="plain"):
    return [summarize(group, tone=tone) for group in groups]


def compact(labels, tone="plain"):
    value = summarize(labels, tone=tone)
    return {"count": value["count"], "score": value["score"]}
