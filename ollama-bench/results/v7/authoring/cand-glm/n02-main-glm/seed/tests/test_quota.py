"""Behavioural checks for quota_gate."""

from linnet.quota_gate import QuotaGateway, build_quota


def test_quota_defaults():
    engine = QuotaGateway()
    assert engine.limit == 12
    assert engine.window_s == 180


def test_quota_seal_is_idempotent():
    engine = QuotaGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaGateway()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
