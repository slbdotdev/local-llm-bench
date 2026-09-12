"""Behavioural checks for tenancy_gate."""

from bollard.tenancy_gate import TenancyLedger, build_tenancy


def test_tenancy_defaults():
    engine = TenancyLedger()
    assert engine.limit == 960
    assert engine.window_s == 45


def test_tenancy_seal_is_idempotent():
    engine = TenancyLedger()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyLedger()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
