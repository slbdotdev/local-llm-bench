"""Metrics calculated from badge-producing workflows."""

from . import core


def count_labels(labels):
    return len(labels)


def tone_counts(labels, tone="plain"):
    values = core.batch(labels, tone=tone)
    return {tone: len(values)}


def measure_groups(groups, tone="plain"):
    built = core.grouped(groups, tone=tone)
    return {"groups": len(built), "items": sum(len(group) for group in built)}


def score(label, tone="plain", weight=1):
    return len(core.make_badge(label, tone=tone)) * weight


def score_all(labels, tone="plain", weight=1):
    return sum(score(label, tone=tone, weight=weight) for label in labels)


def describe_scores(labels, tone="plain"):
    return [score(label, tone=tone) for label in labels]


def report(labels, tone="plain"):
    return {"count": count_labels(labels), "score": score_all(labels, tone=tone),
            "badges": core.batch(labels, tone=tone)}
