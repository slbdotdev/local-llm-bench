"""The middle layer of the badge pipeline."""

import badge_registry


def decorate(label, tone="plain"):
    return badge_registry.add_marker(label, tone=tone)
