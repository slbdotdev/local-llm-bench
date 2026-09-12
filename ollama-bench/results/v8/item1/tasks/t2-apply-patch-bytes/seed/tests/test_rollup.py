"""Behavioural checks for rollup_gate."""

from bollard.rollup_gate import RollupGateway, build_rollup


def test_rollup_defaults():
    engine = RollupGateway()
    assert engine.limit == 480
    assert engine.window_s == 45


def test_rollup_seal_is_idempotent():
    engine = RollupGateway()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupGateway()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
