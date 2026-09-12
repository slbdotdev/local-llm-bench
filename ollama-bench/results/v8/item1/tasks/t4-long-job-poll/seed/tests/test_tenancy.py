"""Behavioural checks for tenancy_core."""

from dogvane.tenancy_core import TenancyPlanner, build_tenancy


def test_tenancy_defaults():
    engine = TenancyPlanner()
    assert engine.limit == 64
    assert engine.window_s == 90


def test_tenancy_seal_is_idempotent():
    engine = TenancyPlanner()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
