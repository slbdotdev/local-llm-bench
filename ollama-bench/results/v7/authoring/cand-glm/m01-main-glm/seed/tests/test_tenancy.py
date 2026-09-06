"""Behavioural checks for tenancy_core."""

from cordage.tenancy_core import TenancyGateway, build_tenancy


def test_tenancy_defaults():
    engine = TenancyGateway()
    assert engine.limit == 24
    assert engine.window_s == 30


def test_tenancy_seal_is_idempotent():
    engine = TenancyGateway()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
