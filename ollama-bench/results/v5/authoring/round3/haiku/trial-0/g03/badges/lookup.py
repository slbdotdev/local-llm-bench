"""Lookup indexes built from several independent record sources."""

from . import core

ALIASES = {"a": "alpha", "b": "beta", "g": "gamma", "d": "delta",
           "e": "epsilon", "z": "zeta", "t": "theta"}


def canonical(name):
    return ALIASES.get(name, name)


def build_index(records, tone="plain"):
    return {canonical(record["key"]): core.make_badge(record["label"], tone=tone)
            for record in records}


def lookup(index, name, default=None):
    return index.get(canonical(name), default)


def lookup_many(index, names, default=None):
    return [lookup(index, name, default=default) for name in names]


def reverse_index(index):
    return {value: key for key, value in index.items()}


def describe_index(index):
    return {"size": len(index), "keys": sorted(index), "values": list(index.values())}


def annotate(records, tone="plain"):
    index = build_index(records, tone=tone)
    return [dict(record, badge=lookup(index, record["key"])) for record in records]
