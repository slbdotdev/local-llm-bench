"""Behavioural checks for checkpoint_gate."""

from cordage.checkpoint_gate import CheckpointRegistry, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointRegistry()
    assert engine.limit == 480
    assert engine.window_s == 30


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointRegistry()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointRegistry()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
