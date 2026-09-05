# Meridian Relay policy evidence

This file belongs to the Meridian Relay repository snapshot used for the 2034 archive
rollout. The repository contains proposals, implementation notes, test fixtures, and
approval history. A value is not current merely because it is precise, appears in code,
or was repeated by a participant. Status, scope, effective revision, and units matter.

The policy concerns the normalized delivery ledger: queryable event retention, the review
schedule, the ordinary implementation spending cap, the late-event alert trigger, the
accountable owner, the committed date, the verification room, and the escalation code.
The emergency override request is a separate change request. It may mention nearby
numbers, but it does not alter the baseline unless the approval history explicitly says
that it was approved and effective. The words draft, proposed, rejected, superseded,
approved, and effective are used deliberately throughout the archive.

When this file cites another record, the citation is a lead to reconcile, not a substitute
for reading the cited record. Dates are calendar dates in UTC. Fractions are stored between
zero and one; percentages in prose are display forms and must not silently replace a
fraction-valued policy field. Dollars are whole US dollars. A team may own an action while
only a named person owns the policy decision.

## Repository map

Repository role: entry point for locating policy evidence and identifying stale material

## Evidence ledger

### Record 01 — 2034-07-01 — Nora Vale

Subject: snapshot boundary

The checked-out tree is the release-candidate evidence pack for the Meridian Relay archive rollout. It includes the source modules, generated examples, operations notes, finance review, compliance interpretations, and a chronological change ledger.

Implication: Read current implementation and approval records together; the tree is intentionally not an answer summary.

### Record 02 — 2034-07-03 — Nora Vale

Subject: authority order

A signed effective approval outranks a draft, a meeting question, a planning forecast, an incident ticket, and a fixture copied from an earlier revision. A rejected emergency request remains useful evidence that a tempting change was not adopted.

Implication: The extraction is about what remains approved, not about collecting every number.

### Record 03 — 2034-07-05 — Ishan Reed

Subject: directory map

The policy schema and runtime modules live under src/meridian. Governance and decision records live under docs/policy and docs/approvals. Finance and compliance records explain units and scope. history/ records superseded revisions; tests/ contains consumers and stale fixtures.

Implication: A solver must reconcile a source tree rather than grep one summary.

### Record 04 — 2034-07-08 — Mara Chen

Subject: baseline scope

The baseline covers ordinary operation of the normalized delivery ledger. It does not include legal holds, forensic exports, or the separately reviewed emergency override request MR-42.

Implication: Do not substitute a special-case lifecycle or request for the ordinary baseline.

### Record 05 — 2034-07-12 — Nora Vale

Subject: release gate

Release gate R-17 requires the eight policy fields to agree across schema, runbook, and approval references. It also requires the repository to retain the trail of discarded candidates for audit.

Implication: Agreement is meaningful only after stale branches and display forms are separated from effective values.

### Record 06 — 2034-07-15 — Jon Bell

Subject: operator warning

The dashboard shows labels chosen for humans: some percentages, some fractions, and some color bands. Those labels are not a second policy source.

Implication: Preserve the canonical unit and scale in the output.

### Record 07 — 2034-07-17 — Mara Chen

Subject: ownership

Action owners in the migration checklist are not the same as the accountable policy owner. The named decision owner is the escalation contact for cross-module disagreement.

Implication: Do not return a team alias or an assignee.

### Record 08 — 2034-07-19 — Release bot

Subject: snapshot

The current release candidate is tagged relay-7.3 and references approval packet AP-17. A later-looking file under history is a simulation of a rejected branch, not a later production approval.

Implication: Use effective status, not file ordering or a lexical maximum date.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
