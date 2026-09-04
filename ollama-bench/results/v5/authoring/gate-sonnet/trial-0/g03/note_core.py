"""Public note writer.

>>> write_note("hello", channel="chat")
'chat:hello'
"""

DEFAULT_CHANNEL = "log"


def write_note(message, *, channel=DEFAULT_CHANNEL, urgent=False):
    return note_bus.forward(message, channel=channel, urgent=urgent)


def bundle(messages, channel=DEFAULT_CHANNEL, sender=write_note, urgent=False):
    return [sender(message, channel=channel, urgent=urgent) for message in messages]


import note_bus
