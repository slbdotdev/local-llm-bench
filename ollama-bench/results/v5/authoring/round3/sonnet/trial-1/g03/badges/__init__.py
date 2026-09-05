"""Public package exports for the badge application."""

from .core import batch, describe, grouped, make_normalized, make_badge
from .flow import decorate
from .registry import reflect

__all__ = ["batch", "describe", "grouped", "make_normalized", "make_badge",
           "decorate", "reflect"]


def make_collection(labels, tone="plain"):
    return batch(labels, tone=tone)


def package_info():
    return {"builder": "make_badge", "default_tone": "plain"}
