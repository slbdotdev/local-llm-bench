"""Compatibility helpers kept for older callers."""
from .planner import build_plan


def make_plan(*args, **kwargs):
    return build_plan(*args, **kwargs)


def is_empty_plan(text):
    return text == ""
