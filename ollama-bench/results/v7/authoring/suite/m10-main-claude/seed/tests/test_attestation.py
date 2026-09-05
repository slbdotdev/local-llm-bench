"""Behavioural checks for attestation_gate."""

from thistle.attestation_gate import AttestationEngine, build_attestation


def test_attestation_defaults():
    engine = AttestationEngine()
    assert engine.limit == 960
    assert engine.window_s == 120


def test_attestation_seal_is_idempotent():
    engine = AttestationEngine()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationEngine()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
