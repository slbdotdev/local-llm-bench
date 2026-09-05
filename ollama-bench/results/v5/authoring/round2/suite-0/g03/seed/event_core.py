"""Public event helpers.

The example is deliberately executable with doctest.

>>> emit_event("alarm", "disk", channel="ops")
'ops|alarm|disk'
"""

DEFAULT_CHANNEL = "main"


def emit_event(kind, payload, channel=DEFAULT_CHANNEL, stamped=False):
    return event_bus.forward(kind, payload, channel=channel, stamped=stamped)


def batch(events, channel=DEFAULT_CHANNEL, stamped=False, sender=emit_event):
    return [sender(event[0], event[1], channel=channel, stamped=stamped)
            for event in events]


# Keep this import late: event_view reflects back to this module.
import event_bus
