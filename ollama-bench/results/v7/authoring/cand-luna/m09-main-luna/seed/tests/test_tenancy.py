"""Behavioural checks for tenancy_flow."""

from harrow.tenancy_flow import TenancyLedger, build_tenancy


def test_tenancy_defaults():
    engine = TenancyLedger()
    assert engine.limit == 250
    assert engine.window_s == 15


def test_tenancy_seal_is_idempotent():
    engine = TenancyLedger()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyLedger()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
