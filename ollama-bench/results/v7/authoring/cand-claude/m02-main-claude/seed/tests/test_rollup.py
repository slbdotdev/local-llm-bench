"""Behavioural checks for rollup_flow."""

from talus.rollup_flow import RollupGateway, build_rollup


def test_rollup_defaults():
    engine = RollupGateway()
    assert engine.limit == 960
    assert engine.window_s == 120


def test_rollup_seal_is_idempotent():
    engine = RollupGateway()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupGateway()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
