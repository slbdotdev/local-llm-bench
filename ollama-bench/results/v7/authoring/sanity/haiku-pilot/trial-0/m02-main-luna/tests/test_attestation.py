"""Behavioural checks for attestation_gate."""

from NorthstarLedger.attestation_gate import AttestationPlanner, build_attestation


def test_attestation_defaults():
    engine = AttestationPlanner()
    assert engine.limit == 96
    assert engine.window_s == 60


def test_attestation_seal_is_idempotent():
    engine = AttestationPlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationPlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
