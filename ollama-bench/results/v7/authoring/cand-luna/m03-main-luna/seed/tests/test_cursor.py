"""Behavioural checks for cursor_gate."""

from wardstone.cursor_gate import CursorLedger, build_cursor


def test_cursor_defaults():
    engine = CursorLedger()
    assert engine.limit == 32
    assert engine.window_s == 90


def test_cursor_seal_is_idempotent():
    engine = CursorLedger()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_cursor_snapshot_is_sorted():
    engine = CursorLedger()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_cursor_reads_the_manifest():
    engine = build_cursor({"cursor": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
