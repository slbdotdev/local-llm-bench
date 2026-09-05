"""Inspection operations expose both source labels and rendered values."""

from .. import core


def inspect(label, tone="plain"):
    return {"input": label, "normalized": core.normalize(label),
            "badge": core.make_tag(label, tone), "tone": tone}


def inspect_many(labels, tone="plain"):
    return [inspect(label, tone=tone) for label in labels]


def normalized_changes(labels):
    return [value for value in inspect_many(labels)
            if value["input"] != value["normalized"]]


def badges(labels, tone="plain"):
    return [value["badge"] for value in inspect_many(labels, tone=tone)]


def summary(labels, tone="plain"):
    values = inspect_many(labels, tone=tone)
    return {"count": len(values), "changed": len(normalized_changes(labels)),
            "badges": [value["badge"] for value in values]}
