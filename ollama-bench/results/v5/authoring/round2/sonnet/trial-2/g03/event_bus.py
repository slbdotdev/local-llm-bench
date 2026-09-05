"""Transport layer for events."""

import event_view


def forward(kind, payload, *, channel="main", stamped=False):
    return event_view.present(kind, payload, channel=channel, stamped=stamped)
