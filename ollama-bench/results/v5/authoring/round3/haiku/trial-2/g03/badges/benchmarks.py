"""Deterministic benchmark samples for badge construction paths."""

from . import core, metrics

SAMPLES = (("tiny", ("A",)), ("pair", ("A", "B")),
           ("mixed", ("Ada", "Bea", "Cy", "Dee")),
           ("long", ("North", "South", "East", "West", "Center")))


def sample(name):
    for sample_name, labels in SAMPLES:
        if sample_name == name:
            return labels
    raise KeyError(name)


def run(name, tone="plain"):
    labels = sample(name)
    values = core.batch(labels, tone=tone)
    return {"name": name, "labels": labels, "values": values,
            "score": metrics.score_all(labels, tone=tone)}


def run_all(tone="plain"):
    return [run(name, tone=tone) for name, _ in SAMPLES]


def names():
    return tuple(name for name, _ in SAMPLES)


def compare(name, first="plain", second="warm"):
    return {"first": run(name, tone=first), "second": run(name, tone=second)}
