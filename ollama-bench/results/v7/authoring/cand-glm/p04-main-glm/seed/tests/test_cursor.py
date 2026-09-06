"""Behavioural checks for cursor_store."""

from latch.cursor_store import CursorEngine, build_cursor


def test_cursor_defaults():
    engine = CursorEngine()
    assert engine.limit == 96
    assert engine.window_s == 180


def test_cursor_seal_is_idempotent():
    engine = CursorEngine()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorEngine()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
