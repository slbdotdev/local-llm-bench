"""Behavioural checks for tenancy_store."""

from cordage.tenancy_store import TenancyEngine, build_tenancy


def test_tenancy_defaults():
    engine = TenancyEngine()
    assert engine.limit == 120
    assert engine.window_s == 45


def test_tenancy_seal_is_idempotent():
    engine = TenancyEngine()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyEngine()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
