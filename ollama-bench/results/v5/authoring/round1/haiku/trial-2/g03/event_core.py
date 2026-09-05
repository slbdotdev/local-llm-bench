"""Public event helpers.

The example is deliberately executable with doctest.

>>> publish_event("disk", "alarm", channel="ops")
'ops|alarm|disk'
"""

DEFAULT_CHANNEL = "main"


def publish_event(payload, kind, *, channel=DEFAULT_CHANNEL, stamped=False):
    return event_bus.forward(kind, payload, channel=channel, stamped=stamped)


def batch(events, channel=DEFAULT_CHANNEL, stamped=False, sender=publish_event):
    return [sender(event[1], event[0], channel=channel, stamped=stamped)
            for event in events]


# Keep this import late: event_view reflects back to this module.
import event_bus
