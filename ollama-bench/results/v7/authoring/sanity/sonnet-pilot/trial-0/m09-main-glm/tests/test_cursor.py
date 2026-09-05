"""Behavioural checks for cursor_core."""

from cinder.cursor_core import CursorPlanner, build_cursor


def test_cursor_defaults():
    engine = CursorPlanner()
    assert engine.limit == 960
    assert engine.window_s == 15


def test_cursor_seal_is_idempotent():
    engine = CursorPlanner()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorPlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
