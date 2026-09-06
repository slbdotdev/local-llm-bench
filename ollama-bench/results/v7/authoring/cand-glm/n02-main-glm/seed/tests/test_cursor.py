"""Behavioural checks for cursor_gate."""

from linnet.cursor_gate import CursorRegistry, build_cursor


def test_cursor_defaults():
    engine = CursorRegistry()
    assert engine.limit == 12
    assert engine.window_s == 90


def test_cursor_seal_is_idempotent():
    engine = CursorRegistry()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorRegistry()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
