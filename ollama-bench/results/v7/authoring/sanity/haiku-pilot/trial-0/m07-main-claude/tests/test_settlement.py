"""Behavioural checks for settlement_view."""

from kestrel.settlement_view import SettlementLedger, build_settlement


def test_settlement_defaults():
    engine = SettlementLedger()
    assert engine.limit == 64
    assert engine.window_s == 120


def test_settlement_seal_is_idempotent():
    engine = SettlementLedger()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_settlement_snapshot_is_sorted():
    engine = SettlementLedger()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_settlement_reads_the_manifest():
    engine = build_settlement({"settlement": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
