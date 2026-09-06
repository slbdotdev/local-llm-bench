"""Behavioural checks for checkpoint_view."""

from quay.checkpoint_view import CheckpointRegistry, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointRegistry()
    assert engine.limit == 960
    assert engine.window_s == 120


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointRegistry()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
