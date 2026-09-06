"""Behavioural checks for rollup_gate."""

from orison.rollup_gate import RollupPlanner, build_rollup


def test_rollup_defaults():
    engine = RollupPlanner()
    assert engine.limit == 96
    assert engine.window_s == 120


def test_rollup_seal_is_idempotent():
    engine = RollupPlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupPlanner()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
