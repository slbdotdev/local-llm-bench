"""Presentation façade used by the application's UI layer."""

from . import core, formatting, themes


def title(label, tone="plain"):
    return core.make_tag(label, tone)


def subtitle(label, tone="muted"):
    return core.make_tag(label, tone)


def card(label, detail="", tone="plain"):
    return {"title": title(label, tone), "detail": detail,
            "footer": subtitle(label, tone="muted")}


def cards(labels, tone="plain"):
    return [card(label, tone=tone) for label in labels]


def themed_card(label, theme_name="default"):
    return {"title": themes.themed(label, theme_name),
            "theme": theme_name}


def list_text(labels, tone="plain"):
    return formatting.render_many(labels, tone=tone, separator=" • ")


def dashboard(labels, tone="plain"):
    return {"cards": cards(labels, tone=tone), "text": list_text(labels, tone=tone)}
