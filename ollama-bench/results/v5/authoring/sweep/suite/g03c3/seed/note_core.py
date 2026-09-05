"""Public note writer.

>>> emit_note("hello", "chat")
'chat:hello'
"""

DEFAULT_CHANNEL = "log"


def emit_note(message, channel=DEFAULT_CHANNEL):
    return note_bus.forward(message, channel=channel)


def bundle(messages, channel=DEFAULT_CHANNEL, sender=emit_note):
    return [sender(message, channel=channel) for message in messages]


import note_bus
