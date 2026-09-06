"""Behavioural checks for backfill_store."""

from kestrel.backfill_store import BackfillEngine, build_backfill


def test_backfill_defaults():
    engine = BackfillEngine()
    assert engine.limit == 480
    assert engine.window_s == 90


def test_backfill_seal_is_idempotent():
    engine = BackfillEngine()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillEngine()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
