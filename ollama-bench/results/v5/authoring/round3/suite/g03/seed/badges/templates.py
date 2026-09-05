"""Named message templates that embed a rendered badge."""

from . import core

TEMPLATES = {
    "short": "{badge}",
    "labeled": "Badge: {badge}",
    "announce": "New badge for {label}: {badge}",
    "change": "Changed {label} to {badge}",
    "warning": "Warning — {badge}",
    "success": "Success — {badge}",
}


def names():
    return tuple(TEMPLATES)


def render(name, label, tone="plain"):
    badge = core.make_tag(label, tone)
    return TEMPLATES[name].format(label=label, badge=badge)


def render_many(name, labels, tone="plain"):
    return [render(name, label, tone=tone) for label in labels]


def choose(label, successful=True, tone="plain"):
    return render("success" if successful else "warning", label, tone=tone)


def all_variants(label, tone="plain"):
    return {name: render(name, label, tone=tone) for name in names()}


def fill(template, label, tone="plain", **values):
    data = dict(values, label=label, badge=core.make_tag(label, tone))
    return template.format(**data)
