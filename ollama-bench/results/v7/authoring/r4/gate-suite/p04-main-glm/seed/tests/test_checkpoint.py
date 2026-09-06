"""Behavioural checks for checkpoint_store."""

from latch.checkpoint_store import CheckpointPlanner, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointPlanner()
    assert engine.limit == 120
    assert engine.window_s == 180


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointPlanner()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointPlanner()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
