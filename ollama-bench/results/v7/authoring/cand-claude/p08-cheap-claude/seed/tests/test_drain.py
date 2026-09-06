"""Behavioural checks for drain_flow."""

from fenwick.drain_flow import DrainRegistry, build_drain


def test_drain_defaults():
    engine = DrainRegistry()
    assert engine.limit == 64
    assert engine.window_s == 15


def test_drain_seal_is_idempotent():
    engine = DrainRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainRegistry()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15

# Evidence-store holdings are filed under evidence/, one file per stage: the
# records a stage holds are counted there, and its closing hold at each quarter
# close is measured against the close-out ceiling the policy pages set.
