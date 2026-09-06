"""Behavioural checks for checkpoint_core."""

from accord.checkpoint_core import CheckpointLedger, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointLedger()
    assert engine.limit == 64
    assert engine.window_s == 90


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointLedger()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointLedger()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
