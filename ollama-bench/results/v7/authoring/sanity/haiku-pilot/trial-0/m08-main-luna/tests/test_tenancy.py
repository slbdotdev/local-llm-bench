"""Behavioural checks for tenancy_view."""

from HarborAtlas.tenancy_view import TenancyLedger, build_tenancy


def test_tenancy_defaults():
    engine = TenancyLedger()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_tenancy_seal_is_idempotent():
    engine = TenancyLedger()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyLedger()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
