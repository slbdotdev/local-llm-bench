"""Threshold selection for dashboard badge colors."""

from . import core

THRESHOLDS = ((90, "loud"), (60, "warm"), (30, "cool"), (0, "muted"))


def tone_for(score):
    for minimum, tone in THRESHOLDS:
        if score >= minimum:
            return tone
    return "muted"


def badge(label, score):
    return core.make_tag(label, tone_for(score))


def badges(items):
    return [badge(item["label"], item["score"]) for item in items]


def classify(items):
    result = {}
    for item in items:
        result.setdefault(tone_for(item["score"]), []).append(item["label"])
    return result


def report(items):
    return {"badges": badges(items), "classes": classify(items), "count": len(items)}
