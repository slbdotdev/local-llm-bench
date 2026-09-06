"""Behavioural checks for checkpoint_gate."""

from arbor.checkpoint_gate import CheckpointPlanner, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointPlanner()
    assert engine.limit == 480
    assert engine.window_s == 120


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
