"""Behavioural checks for quota_view."""

from futtock.quota_view import QuotaLedger, build_quota


def test_quota_defaults():
    engine = QuotaLedger()
    assert engine.limit == 120
    assert engine.window_s == 180


def test_quota_seal_is_idempotent():
    engine = QuotaLedger()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaLedger()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
