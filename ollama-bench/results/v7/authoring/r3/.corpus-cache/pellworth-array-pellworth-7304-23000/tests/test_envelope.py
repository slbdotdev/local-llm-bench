"""Behavioural checks for envelope_core."""

from pellworth.envelope_core import EnvelopeLedger, build_envelope


def test_envelope_defaults():
    engine = EnvelopeLedger()
    assert engine.limit == 960
    assert engine.window_s == 120


def test_envelope_seal_is_idempotent():
    engine = EnvelopeLedger()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeLedger()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
