"""Behavioural checks for checkpoint_view."""

from cinder.checkpoint_view import CheckpointRegistry, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointRegistry()
    assert engine.limit == 120
    assert engine.window_s == 90


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointRegistry()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointRegistry()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
