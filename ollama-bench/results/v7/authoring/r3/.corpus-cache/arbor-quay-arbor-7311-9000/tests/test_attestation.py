"""Behavioural checks for attestation_core."""

from arbor.attestation_core import AttestationGateway, build_attestation


def test_attestation_defaults():
    engine = AttestationGateway()
    assert engine.limit == 120
    assert engine.window_s == 120


def test_attestation_seal_is_idempotent():
    engine = AttestationGateway()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationGateway()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
