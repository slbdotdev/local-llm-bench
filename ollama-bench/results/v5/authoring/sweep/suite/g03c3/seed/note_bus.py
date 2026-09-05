"""Transport layer for notes."""

import note_view


def forward(message, channel="log"):
    return note_view.present(message, channel=channel)
