"""Behavioural checks for rollup_gate."""

from cinder.rollup_gate import RollupEngine, build_rollup


def test_rollup_defaults():
    engine = RollupEngine()
    assert engine.limit == 48
    assert engine.window_s == 60


def test_rollup_seal_is_idempotent():
    engine = RollupEngine()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupEngine()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
