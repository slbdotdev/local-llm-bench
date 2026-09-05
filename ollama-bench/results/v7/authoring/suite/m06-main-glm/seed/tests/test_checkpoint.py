"""Behavioural checks for checkpoint_store."""

from larkspur.checkpoint_store import CheckpointGateway, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointGateway()
    assert engine.limit == 120
    assert engine.window_s == 60


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointGateway()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
