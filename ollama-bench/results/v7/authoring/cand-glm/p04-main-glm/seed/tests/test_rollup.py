"""Behavioural checks for rollup_gate."""

from latch.rollup_gate import RollupRegistry, build_rollup


def test_rollup_defaults():
    engine = RollupRegistry()
    assert engine.limit == 48
    assert engine.window_s == 15


def test_rollup_seal_is_idempotent():
    engine = RollupRegistry()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupRegistry()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
