"""Behavioural checks for checkpoint_flow."""

from opaltelemetry.checkpoint_flow import CheckpointEngine, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointEngine()
    assert engine.limit == 12
    assert engine.window_s == 90


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointEngine()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointEngine()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
