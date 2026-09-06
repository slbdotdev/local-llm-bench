"""Behavioural checks for backfill_gate."""

from kelvin.backfill_gate import BackfillEngine, build_backfill


def test_backfill_defaults():
    engine = BackfillEngine()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_backfill_seal_is_idempotent():
    engine = BackfillEngine()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
