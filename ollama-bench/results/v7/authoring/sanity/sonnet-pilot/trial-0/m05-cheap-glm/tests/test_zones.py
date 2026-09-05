"""Tests for the country-to-zone mapping.

These pin the calculator's inputs, not the rate rules: the rate card is
the specification for the rules themselves (see docs/handover-notes.md for
why there is no rates test).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from kestrel import zones  # noqa: E402


def test_home_market_is_zone_a():
    assert zones.zone_for("de") == "A"
    assert zones.zone_for("NL") == "A"


def test_known_zones():
    assert zones.zone_for("FR") == "B"
    assert zones.zone_for("ES") == "C"
    assert zones.zone_for("SE") == "D"


def test_unknown_country_raises():
    try:
        zones.zone_for("ZZ")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown country")
