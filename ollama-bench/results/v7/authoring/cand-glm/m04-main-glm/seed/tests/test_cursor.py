"""Behavioural checks for cursor_store."""

from vantage.cursor_store import CursorPlanner, build_cursor


def test_cursor_defaults():
    engine = CursorPlanner()
    assert engine.limit == 32
    assert engine.window_s == 120


def test_cursor_seal_is_idempotent():
    engine = CursorPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorPlanner()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
