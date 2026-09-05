"""Integration tests supplied with the badge application."""

import doctest

from badges import core, registry
from badges.adapters import csv, html, plain, slack, terminal
from badges.plugins import console, json_view, markdown, timeline
from badges.services import cache, queue, search, summary


RECORDS = [{"id": 1, "label": "A", "kind": "ok", "keywords": ("first",)},
           {"id": 2, "label": "B", "kind": "warn", "keywords": ("second",)}]


def test_suite():
    assert doctest.testmod(core).failed == 0
    assert core.make_badge("A", tone="red") == "A<red>"
    assert core.batch(["A", "B"], "blue") == ["A<blue>", "B<blue>"]
    assert registry.reflect("C", "green") == "C<green>"
    assert core.grouped([["A"], ["B", "C"]], "muted") == [["A<muted>"], ["B<muted>", "C<muted>"]]
    assert core.describe("D", "warm")["value"] == "D<warm>"
    assert csv.row(RECORDS[0], "cool") == "1,A,A<cool>"
    assert html.badge_span("A", "warm") == '<span class="badge">A&lt;warm&gt;</span>'
    assert plain.block(["A", "B"], "muted") == "A<muted>\nB<muted>"
    assert slack.attachment("A", "loud")["text"] == "A<loud>"
    assert terminal.status("A", tone="cool") == "OK: ~ A<cool>"
    assert console.console_line("A", "ok", "warm") == "[OK] A<warm>"
    assert json_view.view_record(RECORDS[0], "cool")["badge"] == "A<cool>"
    assert markdown.markdown_badge("A", "muted") == "`A<muted>`"
    assert timeline.timeline_event({"year": 2026, "month": 9, "day": 4, "label": "A"}, "plain") == "2026-09-04 A<plain>"
    assert cache.cached(["A", "B"], "warm") == ["A<warm>", "B<warm>"]
    assert queue.queued(["A", "B"], "cool") == ["A<cool>", "B<cool>"]
    assert search.labels(RECORDS, "first", "loud") == ["A"]
    assert summary.compact(["A", "B"], "plain")["count"] == 2


if __name__ == "__main__":
    test_suite()
