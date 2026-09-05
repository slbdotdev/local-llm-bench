"""Onboarding journey facade."""

from .. import core, localization, validation


def welcome(user, language="en", tone="warm"):
    label = localization.translate("hello", language)
    return {"user": user, "badge": core.make_badge(label, tone=tone)}


def step(number, label, tone="plain"):
    return {"step": number, "badge": core.make_badge(label, tone=tone)}


def steps(labels, tone="plain"):
    return [step(number, label, tone=tone) for number, label in enumerate(labels, 1)]


def complete(user, labels, language="en"):
    return {"user": user, "welcome": welcome(user, language),
            "steps": steps(labels, tone="cool"), "ready": bool(labels)}


def validate_labels(labels):
    return [label for label in labels if validation.valid_label(label)]
