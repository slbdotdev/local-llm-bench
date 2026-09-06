"""Behavioural checks for backfill_view."""

from opaltelemetry.backfill_view import BackfillPlanner, build_backfill


def test_backfill_defaults():
    engine = BackfillPlanner()
    assert engine.limit == 250
    assert engine.window_s == 45


def test_backfill_seal_is_idempotent():
    engine = BackfillPlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillPlanner()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
