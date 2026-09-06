"""Behavioural checks for checkpoint_flow."""

from sable.checkpoint_flow import CheckpointGateway, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointGateway()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointGateway()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointGateway()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
