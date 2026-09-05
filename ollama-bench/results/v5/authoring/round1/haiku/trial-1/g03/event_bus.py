"""Transport layer for events."""

import event_view


def forward(payload, kind, *, channel="main", stamped=False):
    return event_view.present(payload, kind, channel=channel, stamped=stamped)
