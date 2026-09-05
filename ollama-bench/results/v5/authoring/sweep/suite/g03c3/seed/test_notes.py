import doctest

import note_core
import note_view


def test_suite():
    assert doctest.testmod(note_core).failed == 0
    assert note_core.emit_note("hello", "chat") == "chat:hello"
    assert note_core.bundle(["a", "b"], "inbox") == ["inbox:a", "inbox:b"]
    assert note_view.reflected("x", "audit") == "audit:x"


if __name__ == "__main__":
    test_suite()
