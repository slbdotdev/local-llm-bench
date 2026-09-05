"""Formatting and reflective entry points."""

import event_core


def present(payload, kind, *, channel="main", stamped=False):
    text = "%s|%s|%s" % (channel, kind, payload)
    return "STAMP " + text if stamped else text


def _fallback(payload, kind, *, channel="main", stamped=False):
    return present(payload, kind, channel=channel, stamped=stamped)


def reflected(event, *, channel="main", stamped=False):
    writer = getattr(event_core, "publish_event", _fallback)
    return writer(event[1], event[0], channel=channel, stamped=stamped)
