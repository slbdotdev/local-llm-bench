"""Catalog operations for the application's named badge definitions."""

from . import core

CATALOG = {
    "alpha": ("Alpha", "cool"),
    "beta": ("Beta", "warm"),
    "gamma": ("Gamma", "muted"),
    "delta": ("Delta", "loud"),
    "epsilon": ("Epsilon", "plain"),
    "zeta": ("Zeta", "cool"),
    "eta": ("Eta", "warm"),
    "theta": ("Theta", "muted"),
}


def names():
    return tuple(CATALOG)


def definition(name):
    return CATALOG[name]


def build(name):
    label, tone = definition(name)
    return core.make_badge(label, tone=tone)


def build_all():
    return {name: build(name) for name in names()}


def select(names_to_build, tone=None):
    result = []
    for name in names_to_build:
        label, catalog_tone = definition(name)
        result.append(core.make_badge(label, tone=catalog_tone if tone is None else tone))
    return result


def search(fragment):
    needle = fragment.lower()
    return [name for name, (label, _) in CATALOG.items()
            if needle in name.lower() or needle in label.lower()]


def catalog_report():
    values = build_all()
    return {"names": list(names()), "values": values, "count": len(values)}
