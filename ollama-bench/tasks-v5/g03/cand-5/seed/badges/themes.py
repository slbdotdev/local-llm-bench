"""Theme definitions and themed badge construction."""

from . import core

THEMES = {
    "default": {"tone": "plain", "prefix": "", "suffix": ""},
    "sunrise": {"tone": "warm", "prefix": "[", "suffix": "]"},
    "ocean": {"tone": "cool", "prefix": "<", "suffix": ">"},
    "paper": {"tone": "muted", "prefix": "{", "suffix": "}"},
    "alarm": {"tone": "loud", "prefix": "!", "suffix": "!"},
}


def theme(name):
    return THEMES[name]


def themed(label, name="default"):
    selected = theme(name)
    badge = core.make_tag(label, selected["tone"])
    return selected["prefix"] + badge + selected["suffix"]


def themed_many(labels, name="default"):
    return [themed(label, name=name) for label in labels]


def theme_names():
    return tuple(THEMES)


def preview(name):
    return themed("Preview", name=name)


def compare(label, first, second):
    return {first: themed(label, first), second: themed(label, second)}
