"""Formatting and reflective entry points."""

import note_core


def present(message, *, channel="log", urgent=False):
    prefix = "URGENT " if urgent else ""
    return "%s%s:%s" % (prefix, channel, message)


def _fallback(message, *, channel="log", urgent=False):
    return present(message, channel=channel, urgent=urgent)


def reflected(message, *, channel="log", urgent=False):
    writer = getattr(note_core, "write_note", _fallback)
    return writer(message, channel=channel, urgent=urgent)
