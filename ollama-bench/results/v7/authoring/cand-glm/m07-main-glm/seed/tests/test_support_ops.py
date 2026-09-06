"""Regression test for the support-tooling bridge. Not part of any pipeline stage's own
test file, and not run by any stage's own test suite."""
from ember.ext import handle_bridge, op_table, trail_writer


def test_lookup_resolves_to_bridge():
    op = op_table.resolve("coalesce")
    assert op is handle_bridge.coalesce


def test_bridge_call_returns_expected_shape():
    result = handle_bridge.coalesce("h-1", payload={"a": 1})
    assert result["op"] == "coalesce"
    assert result["handle_id"] == "h-1"


def test_trail_writer_accepts_the_operation():
    row = trail_writer.serialize_call("coalesce", "h-1")
    assert row["op"] == "coalesce"
