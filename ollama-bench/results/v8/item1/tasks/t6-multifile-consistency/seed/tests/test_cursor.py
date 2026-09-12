"""Behavioural checks for cursor_flow."""

from futtock.cursor_flow import CursorGateway, build_cursor


def test_cursor_defaults():
    engine = CursorGateway()
    assert engine.limit == 960
    assert engine.window_s == 45


def test_cursor_seal_is_idempotent():
    engine = CursorGateway()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorGateway()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
