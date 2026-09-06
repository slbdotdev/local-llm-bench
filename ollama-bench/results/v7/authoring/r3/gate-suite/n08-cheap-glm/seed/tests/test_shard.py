"""Behavioural checks for shard_view."""

from lantern.shard_view import ShardEngine, build_shard


def test_shard_defaults():
    engine = ShardEngine()
    assert engine.limit == 480
    assert engine.window_s == 180


def test_shard_seal_is_idempotent():
    engine = ShardEngine()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardEngine()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
