"""Diagnostic views used when badge output does not match expectations."""

from . import core, validation


def inspect(label, tone="plain"):
    return {"label": label, "normalized": core.normalize(label),
            "tone": tone, "known_tone": core.is_known_tone(tone),
            "badge": core.make_tag(label, tone)}


def inspect_many(labels, tone="plain"):
    return [inspect(label, tone=tone) for label in labels]


def differences(label, tone="plain"):
    value = inspect(label, tone=tone)
    return {key: value[key] for key in ("label", "normalized", "badge")
            if value[key] != value["label"]}


def diagnose(label, tone="plain"):
    value = inspect(label, tone=tone)
    value["errors"] = validation.validate(label, tone=tone)
    value["ready"] = not value["errors"]
    return value


def diagnosis(labels, tone="plain"):
    return {label: diagnose(label, tone=tone) for label in labels}
