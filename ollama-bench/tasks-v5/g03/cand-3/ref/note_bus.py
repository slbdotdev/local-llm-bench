"""Transport layer for notes."""

import note_view


def forward(message, *, channel="log", urgent=False):
    return note_view.present(message, channel=channel, urgent=urgent)
