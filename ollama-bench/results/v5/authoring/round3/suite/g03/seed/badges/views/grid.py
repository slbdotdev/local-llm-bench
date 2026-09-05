"""Grid view with fixed columns."""

from .. import core


def cell(label, tone="plain"):
    return {"text": core.make_tag(label, tone), "width": len(str(label))}


def row(labels, tone="plain"):
    return [cell(label, tone=tone) for label in labels]


def grid(groups, tone="plain"):
    return [row(group, tone=tone) for group in groups]


def widths(groups):
    return [max((len(str(label)) for label in column), default=0)
            for column in zip(*groups)] if groups else []


def grid_summary(groups, tone="plain"):
    value = grid(groups, tone=tone)
    return {"rows": len(value), "widths": widths(groups), "cells": sum(map(len, value))}
