"""Behavioural checks for digest_core."""

from hearth.digest_core import DigestRegistry, build_digest


def test_digest_defaults():
    engine = DigestRegistry()
    assert engine.limit == 64
    assert engine.window_s == 120


def test_digest_seal_is_idempotent():
    engine = DigestRegistry()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestRegistry()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
