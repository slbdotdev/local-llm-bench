"""Behavioural checks for cursor_gate."""

from halyard.cursor_gate import CursorEngine, build_cursor


def test_cursor_defaults():
    engine = CursorEngine()
    assert engine.limit == 12
    assert engine.window_s == 45


def test_cursor_seal_is_idempotent():
    engine = CursorEngine()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorEngine()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
