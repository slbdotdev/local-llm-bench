"""Compatibility boundary used by old integrations during the migration."""

from . import core

legacy_builder = core.make_badge


def compatibility_build(label, tone="plain"):
    return legacy_builder(label, tone)


def compatibility_batch(labels, tone="plain"):
    return [legacy_builder(label, tone) for label in labels]


def choose_builder(prefer="default"):
    choices = {"default": core.make_badge, "legacy": legacy_builder}
    return choices[prefer]


def build_selected(label, prefer="default", tone="plain"):
    return choose_builder(prefer)(label, tone)


def compatibility_record(record, tone="plain"):
    output = dict(record)
    output["badge"] = legacy_builder(record["label"], tone)
    return output
