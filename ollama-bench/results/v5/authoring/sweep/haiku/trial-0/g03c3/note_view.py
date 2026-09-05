"""Formatting and reflective entry points."""

import note_core


def present(message, *, channel="log", urgent=False):
    output = "%s:%s" % (channel, message)
    if urgent:
        output = "URGENT " + output
    return output


def _fallback(message, *, channel="log", urgent=False):
    return present(message, channel=channel, urgent=urgent)


def reflected(message, *, channel="log", urgent=False):
    writer = getattr(note_core, "write_note", _fallback)
    return writer(message, channel=channel, urgent=urgent)
