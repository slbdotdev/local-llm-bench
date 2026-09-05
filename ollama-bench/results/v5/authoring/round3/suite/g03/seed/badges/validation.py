"""Input validation and safe badge construction."""

from . import core


def valid_label(label):
    return isinstance(label, str) and bool(label.strip())


def valid_tone(tone):
    return core.is_known_tone(tone)


def validate(label, tone="plain"):
    errors = []
    if not valid_label(label):
        errors.append("label")
    if not valid_tone(tone):
        errors.append("tone")
    return errors


def safe_make(label, tone="plain"):
    errors = validate(label, tone=tone)
    if errors:
        raise ValueError(",".join(errors))
    return core.make_tag(label, tone)


def safe_batch(labels, tone="plain"):
    return [safe_make(label, tone=tone) for label in labels]


def partition(labels, tone="plain"):
    good, bad = [], []
    for label in labels:
        (good if not validate(label, tone=tone) else bad).append(label)
    return safe_batch(good, tone=tone), bad
