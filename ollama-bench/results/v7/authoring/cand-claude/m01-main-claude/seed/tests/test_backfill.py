"""Behavioural checks for backfill_flow."""

from cinder.backfill_flow import BackfillPlanner, build_backfill


def test_backfill_defaults():
    engine = BackfillPlanner()
    assert engine.limit == 12
    assert engine.window_s == 90


def test_backfill_seal_is_idempotent():
    engine = BackfillPlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillPlanner()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
