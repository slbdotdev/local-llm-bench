"""Behavioural checks for checkpoint_flow."""

from linnet.checkpoint_flow import CheckpointEngine, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointEngine()
    assert engine.limit == 32
    assert engine.window_s == 60


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointEngine()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointEngine()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
