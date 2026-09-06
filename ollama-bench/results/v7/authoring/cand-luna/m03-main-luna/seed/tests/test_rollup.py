"""Behavioural checks for rollup_core."""

from wardstone.rollup_core import RollupPlanner, build_rollup


def test_rollup_defaults():
    engine = RollupPlanner()
    assert engine.limit == 120
    assert engine.window_s == 120


def test_rollup_seal_is_idempotent():
    engine = RollupPlanner()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupPlanner()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
