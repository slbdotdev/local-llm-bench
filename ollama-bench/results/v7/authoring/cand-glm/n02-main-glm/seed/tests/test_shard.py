"""Behavioural checks for shard_flow."""

from linnet.shard_flow import ShardGateway, build_shard


def test_shard_defaults():
    engine = ShardGateway()
    assert engine.limit == 24
    assert engine.window_s == 30


def test_shard_seal_is_idempotent():
    engine = ShardGateway()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardGateway()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
