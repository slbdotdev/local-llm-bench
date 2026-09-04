import doctest

import note_core
import note_view


def test_suite():
    assert doctest.testmod(note_core).failed == 0
    assert note_core.write_note("hello", channel="chat") == "chat:hello"
    assert note_core.write_note("hello", channel="chat", urgent=True) == "URGENT chat:hello"
    assert note_core.bundle(["a", "b"], "inbox") == ["inbox:a", "inbox:b"]
    assert note_view.reflected("x", channel="audit") == "audit:x"
    assert note_view.reflected("x", channel="audit", urgent=True) == "URGENT audit:x"


if __name__ == "__main__":
    test_suite()
