"""p09-main-luna — mode 9, reading past the first screen.

The task follows a regional-retention trail: a glossary definition, a late policy amendment,
and a resolved verification event log must be joined for every region.  The decisive per-region
datum is reconstructed from the component record and event history; it is not written as a
shared constant in an index.
"""
import csv
import datetime
import io
import os
import re
import subprocess
import sys
import textwrap

from .. import common as C

SLOT = "p09-main-luna"
FAMILY = "luna"
MODE = 9
PROJECT = "sable-arc"
PACKAGE = "sable"
CORPUS_SEED = 4909
TARGET_TOKENS = 26500
DELIVERABLE = "retention-report.txt"
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

# There is no per-region module constant in this revision.  Both window facts live in prose
# records, so the index-leak checker is intentionally not applicable.
DECISIVE_CONSTANT = None

GLOSSARY = "docs/retention-glossary.md"
POLICY = "docs/decisions/DR-271-retention.md"
LEDGER = "data/retention-events.csv"
DUMP = "tools/retention_audit.py"
QA_NOTE = "docs/retention-spot-check.md"
AMENDMENT_ID = "DR-271"
QUALIFYING = (2, 7, 13, 18)
EARLY = (4, 11, 20)
WINDOW_DECOY = (1, 9, 16)

_HISTORY_CUES = (
    "Amber spindle settles",
    "Beryl compass settles",
    "Citrine thimble settles",
    "Dahlia prism settles",
    "Elm lantern settles",
    "Fallow quartz settles",
    "Garnet meadow settles",
    "Harbor nickel settles",
    "Indigo kettle settles",
    "Juniper locket settles",
    "Kestrel marble settles",
    "Lilac needle settles",
    "Mica orchard settles",
    "Nacre pebble settles",
    "Ochre ribbon settles",
    "Pewter saffron settles",
    "Quince thistle settles",
    "Russet umber settles",
    "Sable willow settles",
)

_CHANGELOG_CUES = (
    "Amber runtime measure",
    "Beryl runtime measure",
    "Citrine runtime measure",
    "Dahlia runtime measure",
    "Elm runtime measure",
    "Fallow runtime measure",
    "Garnet runtime measure",
    "Harbor runtime measure",
    "Indigo runtime measure",
    "Juniper runtime measure",
    "Kestrel runtime measure",
    "Lilac runtime measure",
    "Mica runtime measure",
    "Nacre runtime measure",
    "Ochre runtime measure",
    "Pewter runtime measure",
    "Quince runtime measure",
    "Russet runtime measure",
    "Sable runtime measure",
)

SUMMARY = """
Write the regional retention report.  The repository's glossary defines which regions are
excluded, the decision record supplies the amendment currently in force, and the retention
event history supplies each region's completed verification date.  Report the excluded regions
in alphabetical order, the sum of their effective retention windows, the governing amendment,
and the verification path stated by the decision record.
"""

BAND_NOTE = "Generated around 26,500 tokens and overlaid with a long glossary, decision record, event ledger, and audit tool to land in the main band."


def _plan(corpus):
    n = len(corpus.stages)
    pick = lambda indexes: [corpus.stages[i % n] for i in indexes]
    return pick(QUALIFYING), pick(EARLY), pick(WINDOW_DECOY)


def _plus(date, days):
    return (datetime.date(*[int(x) for x in date.split("-")]) +
            datetime.timedelta(days=days)).isoformat()


def _base_dates(corpus, qualifying, early):
    q = {s["name"] for s in qualifying}
    e = {s["name"] for s in early}
    out = {}
    for i, stage in enumerate(corpus.stages):
        if stage["name"] in q:
            out[stage["name"]] = "2035-%02d-%02d" % (4 + i % 4, 2 + (i * 3) % 24)
        elif stage["name"] in e:
            # This completed review sits between DR-271's signing date and its effective
            # date.  It makes the amendment date, rather than the heading date, observable.
            if i == EARLY[1]:
                out[stage["name"]] = "2035-03-20"
            else:
                out[stage["name"]] = "2035-%02d-%02d" % (1 + i % 3, 3 + (i * 5) % 24)
        else:
            out[stage["name"]] = "2034-%02d-%02d" % (7 + i % 5, 2 + (i * 7) % 24)
    return out


def _ledger_rows(ctx, qualifying, early):
    corpus = ctx["corpus"]
    qnames = {s["name"] for s in qualifying}
    enames = {s["name"] for s in early}
    dates = _base_dates(corpus, qualifying, early)
    void_q = qualifying[0]["name"]
    void_e = early[0]["name"]
    inflight = early[1]["name"]
    rows = []
    for i, stage in enumerate(corpus.stages):
        name = stage["name"]
        owner = stage["owner"]
        date = dates[name]
        rows.extend([
            (name, "opened", "2033-%02d-%02d" % (1 + i % 8, 2 + i), owner,
             "regional review opened after the seasonal retention survey"),
            (name, "sampled", "2033-%02d-%02d" % (2 + i % 8, 4 + (i * 2) % 22), owner,
             "sample window checked against the archived intake population"),
            (name, "reviewed", "2034-%02d-%02d" % (1 + i % 7, 5 + (i * 3) % 22), owner,
             "reviewer accepted the evidence set for retention assessment"),
        ])
        if name == void_q:
            bad = "2035-03-%02d" % (3 + i)
            rows.extend([
                (name, "verified", bad, owner,
                 "verification recorded before the amended retention rule"),
                (name, "voided", _plus(bad, 9), owner,
                 "voids the verification recorded on %s after a stale sample was found" % bad),
            ])
        rows.extend([
            (name, "verified", date, owner,
             "retention verification completed for the current evidence packet"),
            (name, "countersigned", _plus(date, 7), owner,
             "countersigns verification dated %s after the second reviewer checked provenance" % date),
        ])
        if name == void_e:
            bad = "2035-08-%02d" % (4 + i)
            rows.extend([
                (name, "verified", bad, owner,
                 "verification recorded during a duplicate audit pass"),
                (name, "voided", _plus(bad, 9), owner,
                 "voids the duplicate verification recorded on %s" % bad),
            ])
        if name == inflight:
            rows.append((name, "verified", "2035-09-%02d" % (3 + i), owner,
                         "verification recorded but awaiting the required counter-signature"))
    return sorted(rows, key=lambda row: (row[2], row[0], row[1]))


def _write_ledger(ctx, qualifying, early):
    rows = _ledger_rows(ctx, qualifying, early)
    lines = ["region,event,recorded_on,actor,detail"]
    for row in rows:
        assert not any("," in cell or '"' in cell for cell in row)
        lines.append(",".join(row))
    C.write(os.path.join(ctx["seed"], *LEDGER.split("/")), "\n".join(lines) + "\n")
    C.write(os.path.join(ctx["seed"], *DUMP.split("/")), _DUMP_SOURCE)


def _window_values(index, stage, corpus):
    # Deliberately vary the leading digits: no shared numeric prefix can identify the facts.
    prefixes = (318, 427, 536, 648, 759, 861, 972, 284, 395, 506,
                617, 728, 839, 941, 253, 364, 475, 586, 697)
    effective = prefixes[index] * 1000000000 + index * 1009 + stage["limit"]
    declared = effective
    qnames = {s["name"] for s in _plan(corpus)[0]}
    enames = {s["name"] for s in _plan(corpus)[1]}
    if stage["name"] in qnames:
        declared += 7 + sorted(qnames).index(stage["name"]) * 3
    elif stage["name"] in enames:
        declared += 5 + sorted(enames).index(stage["name"]) * 2
    return declared, effective


_DUMP_SOURCE = r'''"""Resolve the retention event history without changing it."""
import csv
import json
import os
import re

LEDGER = os.path.join("data", "retention-events.csv")
MANIFEST = os.path.join("config", "manifest.json")
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def load():
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def resolve(rows):
    signed, voided = {}, {}
    for row in rows:
        match = DATE.search(row["detail"] or "")
        if not match:
            continue
        if row["event"] == "countersigned":
            signed.setdefault(row["region"], set()).add(match.group(1))
        elif row["event"] == "voided":
            voided.setdefault(row["region"], set()).add(match.group(1))
    answer = {}
    for row in rows:
        if row["event"] != "verified":
            continue
        date = row["recorded_on"]
        if date in voided.get(row["region"], set()):
            continue
        if date not in signed.get(row["region"], set()):
            continue
        answer[row["region"]] = date
    return answer


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    order = [stage["name"] for stage in manifest["stages"]]
    rows = load()
    by_region = {}
    for row in rows:
        by_region.setdefault(row["region"], []).append(row)
    done = resolve(rows)
    rule = "=" * 76
    print("%s regional retention audit" % manifest["project"])
    print("source: %s" % LEDGER)
    print(rule)
    print("%d history records over %d regions, ordered by the manifest." % (len(rows), len(order)))
    print("A verification counts only when its date is countersigned and not voided.")
    print("The audit reports dates only; retention windows remain in component records.")
    for index, name in enumerate(order):
        print("")
        print("[%02d/%02d] %s" % (index + 1, len(order), name))
        for row in by_region.get(name, []):
            print("  %-12s %-14s %-16s %s" %
                  (row["recorded_on"], row["event"], row["actor"], row["detail"]))
        if name in done:
            print("  -> verified_on = %s   (countersigned)" % done[name])
        else:
            print("  -> verified_on = none   (no completed verification)")
    print("")
    print(rule)
    print("%d of %d regions have completed verification." % (len(done), len(order)))


if __name__ == "__main__":
    main()
'''


def overlay(ctx):
    corpus = ctx["corpus"]
    qualifying, early, window_decoy = _plan(corpus)
    for i, stage in enumerate(corpus.stages):
        declared, effective = _window_values(i, stage, corpus)
        src = C.read(corpus.path(stage["src"]))
        src, removed = re.subn(r"^EFFECTIVE_RETENTION_DAYS = .*\n?", "", src, count=1, flags=re.M)
        assert removed == 1
        C.write(corpus.path(stage["src"]), src)
        doc = C.read(corpus.path(stage["doc"]))
        doc, removed = re.subn(r"^\| `regional_window` \|[^\n]*\n?", "", doc, count=1, flags=re.M)
        assert removed == 1
        C.write(corpus.path(stage["doc"]), doc)
        history = C.read(corpus.path(stage["history"]))
        history_line = "%s at %d days." % (_HISTORY_CUES[i], declared)
        # Keep the new prose away from the generated heading and its ordinary vocabulary so
        # the roster check cannot harvest it by proximity.
        C.write(corpus.path(stage["history"]), history.rstrip("\n") + "\n" * 8 + history_line + "\n")
        if i == 0:
            changelog = C.read(corpus.path("history/CHANGELOG.md"))
            changelog += "\n" * 8
        changelog += "- `%s`: %s at %d days.\n" % (stage["module"], _CHANGELOG_CUES[i], effective)
    C.write(corpus.path("history/CHANGELOG.md"), changelog)
    for i, stage in enumerate(window_decoy):
        corpus.set_doc_window(stage, stage["window"] + 19 + i)
    _write_ledger(ctx, qualifying, early)
    _write_glossary(ctx)
    _write_policy(ctx)
    _write_qa(ctx, window_decoy)
    corpus.append("README.md", _readme_addendum())


def _entry(term, body, extra=()):
    lines = ["## " + term, ""] + textwrap.wrap(body, width=92)
    for item in extra:
        lines += [""] + textwrap.wrap(item, width=92)
    return lines + [""]


_GLOSSARY_ENTRIES = [
    ("accepted sample", "Evidence retained after a reviewer confirms that the observed intake is representative."),
    ("amended rule", "A dated project decision that changes which completed reviews may be reported."),
    ("archive window", "The ordinary interval used by the archive service, not the regional retention window."),
    ("audit packet", "The bounded collection of records a reviewer checks before signing a verification."),
    ("calendar date", "The recorded day of an event; it is not automatically the date on which an event became valid."),
    ("component record", "The document beside a region's module that records the window communicated to operators."),
    ("completed verification", "A verification event named by a countersignature and not cancelled by a voiding event."),
    ("countersignature", "A second review that names the date of the verification it accepts."),
    ("declared window", "The retention interval stated in a region's historical operator note."),
    ("effective window", "The interval the running module actually uses when no optional override is enabled."),
    ("event history", "An append-only sequence from which a current review state is resolved rather than copied."),
    ("evidence packet", "The records a reviewer uses to decide whether a regional sample can be trusted."),
    ("expired review", "A review whose evidence no longer describes the current intake; it is kept for history."),
    ("in-flight verification", "A recorded verification that has neither been voided nor countersigned yet."),
    ("manifest region", "A region named by the repository manifest and therefore included in a quarterly sweep."),
    ("operational window", "A human-facing value in an operations table; it is not the module's effective value."),
    ("override", "An explicitly enabled runtime option, distinct from the default interval in a module."),
    ("policy record", "A dated decision document that determines how a defined project term is reported."),
    ("prior review", "A superseded review retained so that later decisions can cite what changed."),
    ("regional record", "The component document and event history associated with one manifest region."),
    ("reported region", "A region whose history and component evidence satisfy the active reporting rule."),
    ("retention interval", "The number of days for which the service keeps a region's accepted records."),
    ("review date", "The date a reviewer records an event, which may differ from the date the event is accepted."),
    ("sample correction", "A later note explaining why an earlier review attempt should not survive."),
    ("seasonal intake", "The varying arrival pattern used when the retention survey chooses its evidence packet."),
    ("signed event", "An event whose date is explicitly named by a countersigning record."),
    ("superseded decision", "A decision retained for provenance but no longer governing current reports."),
    ("voided event", "A record that cancels an earlier event by naming its recorded date."),
    ("annual review", "The scheduled review that checks whether regional evidence still supports the stated interval."),
    ("batch boundary", "The point at which one intake batch ends and the next batch may be assessed."),
    ("control note", "A short operational note that records a check without becoming a policy ruling."),
    ("date window", "A range used to search the history; it is not itself a retention decision."),
    ("evidence owner", "The person responsible for preserving the packet, not the person who sets policy."),
    ("historical correction", "A recorded explanation for replacing an earlier review attempt."),
    ("intake boundary", "The boundary used to separate one regional sample from another."),
    ("ledger order", "The stable order in which events are presented after they are read from the ledger."),
    ("module default", "The value used by the running component when no explicit override is enabled."),
    ("narrow review", "A review of one packet or region, not the complete manifest sweep."),
    ("operator note", "A human-facing observation which cannot supersede a dated decision."),
    ("packet signature", "A record that a reviewer accepted the evidence packet for further processing."),
    ("quarterly sweep", "The complete review over every region in the repository manifest."),
    ("recorded interval", "The interval preserved in a component document for audit comparison."),
    ("retention audit", "The read-only operation that resolves history and supplies verification dates."),
    ("sample provenance", "The source trail by which a reviewer can reproduce the evidence packet."),
    ("source authority", "The project rule that says which artifact decides a particular kind of disagreement."),
    ("status note", "A descriptive note about a review, not proof that the review completed."),
    ("verification attempt", "A dated attempt which may later be voided or completed by countersignature."),
    ("window disagreement", "A difference between an operator-facing interval and the module's effective interval."),
]

_DECIDING = ("regional retention", "The project's reporting term. A region is excluded when its declared window differs from its effective window and its completed verification is dated on or after the active amendment's effective date. The definition is authoritative here; a slide, component prose, or ordinary English is not.", ["A region with only an in-flight verification is not completed. A voided verification is not the completed one."])


def _write_glossary(ctx):
    lines = ["# Retention glossary", "", "Definitions are alphabetical project vocabulary; each entry is included so a reviewer can distinguish operational prose from the reporting rule.", "This glossary is deliberately comprehensive because the same ordinary word can carry a narrower meaning in an audit.", "Readers should follow the dated decision and the event resolver after identifying the defined term.", ""]
    for term, body in _GLOSSARY_ENTRIES:
        lines += _entry(term, body)
    lines += _entry(*_DECIDING)
    C.write(os.path.join(ctx["seed"], *GLOSSARY.split("/")), "\n".join(lines))


def _write_policy(ctx):
    filler = []
    for title in ("Evidence ownership", "How operators use the report", "History and scope", "Review cadence", "Why the old rule failed", "Audit boundaries"):
        filler += ["## " + title, "", "The review group records its reasoning here so that a later reader can distinguish a current ruling from a historical observation.", "The glossary owns the meaning of the reporting term; this record owns the date and authority of the amendment.", "", "The report does not repair component records, and a history entry is evidence rather than a current instruction.", ""]
    lines = ["# DR-271 — regional retention decision", "", "- Status: **in force**", "- Applies to: every region named by the repository manifest", "", "## Authority", "", "This record identifies the active amendment and its reporting path. The retention glossary carries the definition of the project term; this record deliberately does not repeat that definition.", "", "The verification audit resolves event history. A date in a narrative note is not a completed verification unless the event history supplies the countersignature.", ""] + filler
    lines += ["## Amendment register", "", "### DR-266 — 2034-11-08 — superseded", "", "The first register treated the component record as authoritative. That rule was retired when the running module became the operational source.", "", "### DR-270 — 2035-02-12 — withdrawn", "", "A draft would have reported every window disagreement, including reviews that predated the new evidence process. It was withdrawn before adoption.", "", "### DR-271 — 2035-03-14 — **in force**", "", "The current amendment takes effect on **2035-04-01**. Cite DR-271 when a report uses this amendment. The verification path is: glossary > decision record > resolved event audit.", "", "The date is the amendment's effective date, not the date on which this record was signed.", ""]
    C.write(os.path.join(ctx["seed"], *POLICY.split("/")), "\n".join(lines))


def _write_qa(ctx, window_decoy):
    names = sorted(s["name"] for s in window_decoy)
    lines = ["# Retention spot check", "", "This is a lead from an old review slide, not a ruling. It compared operational windows and did not resolve the component evidence.", "", "Regions on the old slide:", ""]
    lines += ["- " + name for name in names]
    lines += ["", "The slide is retained to explain why a quick window-only sweep is not a regional retention report.", ""]
    C.write(os.path.join(ctx["seed"], *QA_NOTE.split("/")), "\n".join(lines))


def _readme_addendum():
    return """## Retention review material

- `docs/retention-glossary.md` — definitions, including the project's reporting term.
- `docs/decisions/` — dated policy records; the latest active record controls the reporting date.
- `data/retention-events.csv` — append-only review history. Resolve it with `python tools/retention_audit.py`.
- `history/00NN-<region>.md` — each region's operator-facing interval note.
- `history/CHANGELOG.md` — the module-facing interval note for each region.
- `docs/retention-spot-check.md` — a non-authoritative old window comparison.
"""


def _resolved_dates(corpus):
    rows = list(csv.DictReader(io.StringIO(C.read(corpus.path(LEDGER)))))
    signed, voided = {}, {}
    for row in rows:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", row["detail"] or "")
        if not match:
            continue
        if row["event"] == "countersigned":
            signed.setdefault(row["region"], set()).add(match.group(1))
        elif row["event"] == "voided":
            voided.setdefault(row["region"], set()).add(match.group(1))
    out = {}
    for row in rows:
        if row["event"] != "verified":
            continue
        date = row["recorded_on"]
        if date in voided.get(row["region"], set()) or date not in signed.get(row["region"], set()):
            continue
        assert row["region"] not in out
        out[row["region"]] = date
    assert set(out) == {s["name"] for s in corpus.stages}
    return out


def _naive_dates(corpus, which):
    rows = list(csv.DictReader(io.StringIO(C.read(corpus.path(LEDGER)))))
    voided = {}
    for row in rows:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", row["detail"] or "")
        if row["event"] == "voided" and match:
            voided.setdefault(row["region"], set()).add(match.group(1))
    out = {}
    for row in rows:
        if row["event"] != "verified":
            continue
        if which == "first":
            out.setdefault(row["region"], row["recorded_on"])
        elif which == "unvoided" and row["recorded_on"] in voided.get(row["region"], set()):
            continue
        else:
            out[row["region"]] = max(out.get(row["region"], ""), row["recorded_on"])
    return out


def _prose_value(corpus, stage, cues, source):
    text = C.read(corpus.path(source(stage)))
    cue = cues[corpus.stages.index(stage)]
    match = re.search(r"^%s at (\d+) days\.$" % re.escape(cue), text, re.M)
    assert match, (stage["name"], source(stage), cue)
    return int(match.group(1))


def _declared_value(corpus, stage):
    return _prose_value(corpus, stage, _HISTORY_CUES, lambda s: s["history"])


def _module_value(corpus, stage):
    return _prose_value(corpus, stage, _CHANGELOG_CUES, lambda _s: "history/CHANGELOG.md")


def _policy_dates(corpus):
    text = C.read(corpus.path(POLICY))
    signed = re.search(r"^### %s — (\d{4}-\d{2}-\d{2}) —" % AMENDMENT_ID, text, re.M)
    effective = re.search(r"current amendment takes effect on \*\*(\d{4}-\d{2}-\d{2})\*\*", text)
    assert signed and effective
    return {"signed": signed.group(1), "effective": effective.group(1)}


def _excluded(ctx, dates=None, effective_from=None):
    corpus = ctx["corpus"]
    dates = dates or _resolved_dates(corpus)
    effective_from = effective_from or _policy_dates(corpus)["effective"]
    out = []
    for stage in corpus.stages:
        if _declared_value(corpus, stage) != _module_value(corpus, stage):
            if dates[stage["name"]] >= effective_from:
                out.append(stage)
    return sorted(out, key=lambda s: s["name"])


def _audit_output(ctx):
    result = subprocess.run([sys.executable, os.path.join("tools", "retention_audit.py")], cwd=ctx["seed"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr[-400:]
    return result.stdout


def facts(ctx):
    corpus = ctx["corpus"]
    dates = _resolved_dates(corpus)
    policy_dates = _policy_dates(corpus)
    excluded = _excluded(ctx, dates, policy_dates["effective"])
    assert len(excluded) == len(QUALIFYING)
    glossary = C.read(corpus.path(GLOSSARY))
    entry = "## regional retention"
    assert entry in glossary
    entry_line = glossary[:glossary.index(entry)].count("\n") + 1
    assert entry_line > 200, (entry_line, len(glossary.splitlines()))
    policy = C.read(corpus.path(POLICY))
    amend_at = policy.index("### %s" % AMENDMENT_ID)
    assert amend_at > len(policy) // 2
    audit = _audit_output(ctx)
    assert 6000 < len(audit) < 24000
    marks = []
    for stage in excluded:
        marker = "] %s" % stage["name"]
        at = audit.index(marker)
        date_at = audit.index("-> verified_on = %s" % dates[stage["name"]], at)
        marks.append(date_at)
    deepest = max(marks)
    assert deepest > 6000
    match = re.search(r"The verification path is: (.+)\.", policy)
    assert match
    path = match.group(1).strip()
    names = [s["name"] for s in excluded]
    total = sum(_module_value(corpus, s) for s in excluded)
    return {
        "keys": ["effective_window", "governing_amendment", "excluded_region", "verification_path"],
        "expect": {
            "effective_window": str(total),
            "governing_amendment": AMENDMENT_ID,
            "excluded_region": ", ".join(names),
            "verification_path": path,
        },
        "kinds": {"effective_window": "int", "governing_amendment": "ci", "excluded_region": "list", "verification_path": "loose"},
        "groups": [
            {"name": "the effective window total", "keys": ["effective_window"]},
            {"name": "the active amendment", "keys": ["governing_amendment"]},
            {"name": "the excluded region set", "keys": ["excluded_region"]},
            {"name": "the verification path", "keys": ["verification_path"]},
        ],
        "names": names,
        "total": total,
        "dates": dates,
        "entry_line": entry_line,
        "glossary_lines": len(glossary.splitlines()),
        "audit_chars": len(audit),
        "audit_lines": len(audit.splitlines()),
        "audit_deepest": deepest,
        "ledger_chars": len(C.read(corpus.path(LEDGER))),
        "ledger_rows": len(C.read(corpus.path(LEDGER)).splitlines()) - 1,
    }


def harvest_units(ctx):
    corpus = ctx["corpus"]
    units = []
    for stage in corpus.stages:
        # These are separate declarations: the two window inputs are the per-unit facts used
        # by the predicate.  Verification dates are resolved from the ledger and are not
        # joined into either value.
        units.append({"unit": "%s declared" % stage["name"],
                      "value": str(_declared_value(corpus, stage)),
                      "path": stage["history"]})
        units.append({"unit": "%s effective" % stage["name"],
                      "value": str(_module_value(corpus, stage)),
                      "path": "history/CHANGELOG.md"})
    assert len(units) >= 6 and len({u["unit"] for u in units}) == len(units)
    return units


def prompt(ctx):
    return """# Regional retention report

You are working at the root of the `sable-arc` repository. Every region named by the repository
manifest is in scope. Read the project's glossary, the active dated decision, each region's own
history entry, the history changelog, and the resolved retention event history. The old spot-check
page is only a lead. Apply the project's definition of **regional retention**, then apply the
amendment that is currently in force. A verification is complete only under the repository's
stated event-history rule.

Write a new file `retention-report.txt` in the repository root with exactly these four lines, in
this order:

    effective_window: <the sum of the effective windows for excluded regions, as a plain integer>
    governing_amendment: <the identifier of the active amendment>
    excluded_region: <excluded region names in alphabetical order, separated by commas>
    verification_path: <the path stated by the active decision record>

The file may or may not end with a newline. Do not add a header, explanation, quotes, or other
lines. Do not modify or delete any existing file, and create no file other than the report.
"""


def reference(ctx):
    f = ctx["facts"]
    return {DELIVERABLE: "effective_window: %s\ngoverning_amendment: %s\nexcluded_region: %s\nverification_path: %s\n" % (
        f["expect"]["effective_window"], f["expect"]["governing_amendment"], f["expect"]["excluded_region"], f["expect"]["verification_path"])}


def editable(ctx):
    return []


def sweep_paths(ctx):
    corpus = ctx["corpus"]
    paths = [GLOSSARY, POLICY, LEDGER, DUMP, QA_NOTE, "config/manifest.json", "README.md",
             "history/CHANGELOG.md"]
    for stage in corpus.stages:
        paths.append(stage["history"])
    return paths


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": GLOSSARY, "hop": "definition", "why": "defines regional retention and the exclusion predicate"},
        {"path": POLICY, "hop": "ruling", "why": "records the active amendment and verification path"},
        {"path": LEDGER, "hop": "history", "why": "carries the per-region verification events"},
        {"path": DUMP, "hop": "resolution", "why": "resolves completed, countersigned, unvoided verification dates"},
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True, "why": "defines the regions in scope"},
        {"path": QA_NOTE, "hop": "decoy", "why": "rules out the tempting window-only spot check"},
        {"path": "history/CHANGELOG.md", "hop": "effective-window", "why": "carries each module-facing interval in prose"},
    ]
    for stage in corpus.stages:
        lb.append({"path": stage["history"], "hop": "declared-window", "why": "operator-facing interval for the region"})
    return lb


def _answer(ctx, names=None, total=None, amendment=AMENDMENT_ID, path=None):
    f = ctx["facts"]
    return "effective_window: %s\ngoverning_amendment: %s\nexcluded_region: %s\nverification_path: %s\n" % (
        str(f["total"] if total is None else total), amendment,
        f["expect"]["excluded_region"] if names is None else ", ".join(names),
        f["expect"]["verification_path"] if path is None else path)


_PERTURBATIONS = [
    ("no trailing newline", lambda text: text.rstrip("\n")),
    ("two trailing newlines", lambda text: text + "\n"),
    ("CRLF line endings", lambda text: text.replace("\n", "\r\n")),
    ("one leading blank line", lambda text: "\n" + text),
    ("trailing spaces on every line", lambda text: "\n".join((line + "  ") if line.strip() else line for line in text.split("\n"))),
]


def probes(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    policy_dates = _policy_dates(corpus)
    effective_from = policy_dates["effective"]
    signed_from = policy_dates["signed"]
    ref = reference(ctx)[DELIVERABLE]
    full = "%d/%d" % (3 + len(f["groups"]) + 1, 3 + len(f["groups"]) + 1)
    divergent = sorted(s["name"] for s in corpus.stages if _declared_value(corpus, s) != _module_value(corpus, s))
    declared_total = sum(_declared_value(corpus, corpus.by_name[n]) for n in f["names"])
    first = _naive_dates(corpus, "first")
    first_names = sorted(s["name"] for s in corpus.stages if _declared_value(corpus, s) != _module_value(corpus, s) and first.get(s["name"], "0000") >= effective_from)
    last = _naive_dates(corpus, "last")
    last_names = sorted(s["name"] for s in corpus.stages if _declared_value(corpus, s) != _module_value(corpus, s) and last.get(s["name"], "0000") >= effective_from)
    signed_names = sorted(s["name"] for s in corpus.stages if _declared_value(corpus, s) != _module_value(corpus, s) and f["dates"].get(s["name"], "0000") >= signed_from)
    assert set(first_names) != set(f["names"]) and set(last_names) != set(f["names"])
    assert set(signed_names) != set(f["names"])
    window_names = sorted(s["name"] for s in _plan(corpus)[2])
    window_total = sum(_module_value(corpus, corpus.by_name[n]) for n in window_names)
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref}, "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed", "no_traceback": True},
        {"name": "wrong: every divergence, amendment ignored", "files": {DELIVERABLE: _answer(ctx, divergent, sum(_module_value(corpus, corpus.by_name[n]) for n in divergent))}, "verdict": "confidently_wrong"},
        {"name": "wrong: first verification row used", "files": {DELIVERABLE: _answer(ctx, first_names, sum(_module_value(corpus, corpus.by_name[n]) for n in first_names))}, "verdict": "confidently_wrong"},
        {"name": "wrong: latest verification row used", "files": {DELIVERABLE: _answer(ctx, last_names, sum(_module_value(corpus, corpus.by_name[n]) for n in last_names))}, "verdict": "confidently_wrong"},
        {"name": "wrong: amendment signing date used", "files": {DELIVERABLE: _answer(ctx, signed_names, sum(_module_value(corpus, corpus.by_name[n]) for n in signed_names))}, "verdict": "confidently_wrong"},
        {"name": "wrong: spot check trusted", "files": {DELIVERABLE: _answer(ctx, window_names, window_total, "DR-270")}, "verdict": "confidently_wrong"},
        {"name": "wrong: declared windows summed", "files": {DELIVERABLE: _answer(ctx, total=declared_total)}, "verdict": "confidently_wrong"},
        {"name": "shape: keys in wrong order", "files": {DELIVERABLE: "governing_amendment: %s\neffective_window: %s\nexcluded_region: %s\nverification_path: %s\n" % (f["expect"]["governing_amendment"], f["expect"]["effective_window"], f["expect"]["excluded_region"], f["expect"]["verification_path"])}, "verdict": "confidently_wrong"},
    ]
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)}, "verdict": "correct", "score": full})
    return cases


def notes(ctx, m):
    f = ctx["facts"]
    lb = "\n".join("- `%s` — %s (*%s*)" % (item["path"], item["why"], item["hop"]) for item in m["load_bearing"])
    return """# NOTES — %(slot)s (mode %(mode)d)

## 1. Failure mode

Mode 9, reading past the first screen. The task measures whether a model reads the glossary's
late definition and then reads the long resolved audit output far enough to obtain every needed
verification date. It is a positive answer: the report names excluded regions.

## 2. Distinguishing condition

A shallow solve trusts the old spot check, copies the first plausible definition, or takes the
first/latest verification row. The material rules those out with an explicit glossary rule, a
dated active amendment, and a countersigned/non-voided event-history resolver. The decisive
glossary heading is at line %(entry_line)d of %(glossary_lines)d; the resolved audit is %(audit_chars)d
characters over %(audit_lines)d lines, and the deepest needed date is at character %(deepest)d.
The output stays below the 24,000-character truncation threshold, so the intended treatment is
placement rather than narrowing.

## 3. Grader soundness

The grader checks existence/UTF-8, exact four-key shape and order, one independent group per
reported fact, and the integrity/scope gate. Its probes cover an untouched sandbox, five
wrong-but-plausible courses, wrong key order, and all five formatting perturbations. The
reference is derived from the seed; no expected value is typed independently.

## 4. Near-miss table

| outcome | result |
| --- | --- |
| reference | correct, full score |
| untouched sandbox | visibly_failed, no traceback |
| divergence set / first row / latest row / spot check / declared total | confidently_wrong |
| wrong key order | confidently_wrong |
| no newline / two newlines / CRLF / leading blank / trailing spaces | correct, full score |

## 5. Anti-harvest and rung 0

Mechanism 2 (derived from records, never stated) is used for all %(units)d harvest units: each
unit's declared window, effective window, and completed verification date are joined into the
decisive composite only by reading seed/ and replaying the event history. Mechanism 3 is also
used: the roster pointer is the only named load-bearing file, while the glossary, decision,
ledger, and audit tool are reached through repository links. Mechanism 4 supplies the decoy
window note. No shared constant states the answer, and the sweep reaches %(sweep)d of %(tokens)d
material tokens (%(sweeppct)s%%).

Load-bearing declaration: %(lb_count)d paths over %(hop_count)d hops.

%(lb)s

## 6. Budget and departures

This is a main-band task, not mode 8; a reasonable solve is under 300 seconds and under 5,000
output tokens. The research idea called for the names `effective_window`, `governing_amendment`,
`excluded_region`, and `verification_path`; this candidate keeps that shape, while making the
per-region value a replayed composite and using a countersigned event audit so the second mode-9
fact is genuinely in a long command output. No material departure was required.

## Derivability

All four reference values are measured from seed/: the region set joins each component record to
each module and resolved event date, the total sums measured module values, the amendment and
path are read from the active decision record. No answer value is asserted from memory.
""" % {"slot": SLOT, "mode": MODE, "entry_line": f["entry_line"], "glossary_lines": f["glossary_lines"], "audit_chars": f["audit_chars"], "audit_lines": f["audit_lines"], "deepest": f["audit_deepest"], "units": len(harvest_units(ctx)), "sweep": m["sweep_tokens"], "tokens": m["tokens"], "sweeppct": m["sweep_pct"], "lb_count": len(m["load_bearing"]), "hop_count": len(set(item["hop"] for item in m["load_bearing"])), "lb": lb}
