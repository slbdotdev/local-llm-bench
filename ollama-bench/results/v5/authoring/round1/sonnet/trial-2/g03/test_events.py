import doctest

import event_core
import event_view


def test_suite():
    assert doctest.testmod(event_core).failed == 0
    assert event_core.emit_event("alarm", "disk", channel="ops") == "ops|alarm|disk"
    assert event_core.batch([("a", "one"), ("b", "two")]) == ["main|a|one", "main|b|two"]
    assert event_view.reflected(("notice", "cache"), channel="audit", stamped=True) == "STAMP audit|notice|cache"


if __name__ == "__main__":
    test_suite()
