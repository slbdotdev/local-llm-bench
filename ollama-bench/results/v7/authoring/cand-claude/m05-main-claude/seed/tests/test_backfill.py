"""Behavioural checks for backfill_view."""

from hearth.backfill_view import BackfillEngine, build_backfill


def test_backfill_defaults():
    engine = BackfillEngine()
    assert engine.limit == 64
    assert engine.window_s == 15


def test_backfill_seal_is_idempotent():
    engine = BackfillEngine()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillEngine()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
