"""Behavioural checks for shard_core."""

from kestrel.shard_core import ShardEngine, build_shard


def test_shard_defaults():
    engine = ShardEngine()
    assert engine.limit == 48
    assert engine.window_s == 60


def test_shard_seal_is_idempotent():
    engine = ShardEngine()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardEngine()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
