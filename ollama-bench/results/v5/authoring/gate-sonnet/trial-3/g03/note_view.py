"""Formatting and reflective entry points."""

import note_core


def present(message, channel="log"):
    return "%s:%s" % (channel, message)


def _fallback(message, channel="log"):
    return present(message, channel=channel)


def reflected(message, channel="log"):
    writer = getattr(note_core, "emit_note", _fallback)
    return writer(message, channel=channel)
