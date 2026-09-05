"""Behavioural checks for shard_view."""

from thistle.shard_view import ShardGateway, build_shard


def test_shard_defaults():
    engine = ShardGateway()
    assert engine.limit == 64
    assert engine.window_s == 90


def test_shard_seal_is_idempotent():
    engine = ShardGateway()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardGateway()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
