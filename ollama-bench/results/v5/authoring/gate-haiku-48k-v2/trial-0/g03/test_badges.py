import doctest

import badge_core
import badge_registry


def test_suite():
    assert doctest.testmod(badge_core).failed == 0
    assert badge_core.make_badge("A", tone="red") == "A<red>"
    assert badge_core.batch(["A", "B"], tone="blue") == ["A<blue>", "B<blue>"]
    assert badge_registry.reflect("C", tone="green") == "C<green>"


if __name__ == "__main__":
    test_suite()
