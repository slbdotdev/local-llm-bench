"""Behavioural checks for shard_store."""

from cinder.shard_store import ShardEngine, build_shard


def test_shard_defaults():
    engine = ShardEngine()
    assert engine.limit == 96
    assert engine.window_s == 45


def test_shard_seal_is_idempotent():
    engine = ShardEngine()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardEngine()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
