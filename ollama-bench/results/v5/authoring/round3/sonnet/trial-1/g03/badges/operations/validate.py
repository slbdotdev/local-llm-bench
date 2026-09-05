"""Batch validation operations."""

from .. import core, validation


def check_labels(labels, tone="plain"):
    return [{"label": label, "valid": not validation.validate(label, tone=tone),
             "badge": core.make_badge(label, tone=tone)} for label in labels]


def valid_badges(labels, tone="plain"):
    return [item["badge"] for item in check_labels(labels, tone=tone) if item["valid"]]


def invalid_labels(labels, tone="plain"):
    return [item["label"] for item in check_labels(labels, tone=tone) if not item["valid"]]


def report(labels, tone="plain"):
    values = check_labels(labels, tone=tone)
    return {"total": len(values), "valid": sum(item["valid"] for item in values),
            "invalid": invalid_labels(labels, tone=tone)}
