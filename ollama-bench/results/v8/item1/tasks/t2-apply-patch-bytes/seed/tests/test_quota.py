"""Behavioural checks for quota_store."""

from bollard.quota_store import QuotaRegistry, build_quota


def test_quota_defaults():
    engine = QuotaRegistry()
    assert engine.limit == 96
    assert engine.window_s == 30


def test_quota_seal_is_idempotent():
    engine = QuotaRegistry()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaRegistry()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
