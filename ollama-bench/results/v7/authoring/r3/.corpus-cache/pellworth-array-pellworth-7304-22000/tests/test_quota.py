"""Behavioural checks for quota_gate."""

from pellworth.quota_gate import QuotaLedger, build_quota


def test_quota_defaults():
    engine = QuotaLedger()
    assert engine.limit == 24
    assert engine.window_s == 90


def test_quota_seal_is_idempotent():
    engine = QuotaLedger()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaLedger()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
