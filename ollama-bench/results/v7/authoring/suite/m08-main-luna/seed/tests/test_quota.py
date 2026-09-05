"""Behavioural checks for quota_flow."""

from HarborAtlas.quota_flow import QuotaLedger, build_quota


def test_quota_defaults():
    engine = QuotaLedger()
    assert engine.limit == 12
    assert engine.window_s == 30


def test_quota_seal_is_idempotent():
    engine = QuotaLedger()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaLedger()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
