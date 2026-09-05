# 2025-10: legacy migration

Status: ARCHIVED.
Record identifier: rc-202510-09.
This review record is part of the release-control history. It is intentionally
detailed because incident response and replay compare decisions across schema
revisions. V1 and V2 records may contain legacy_any and owner aliases. Migration maps fields but does not transfer legacy aggregation into the current evaluator. The migration report must retain the source revision for audit, not alter the current rule's meaning.

## Reading rule

For a current decision, read the current source path named by the public entry
point and assemble one frozen snapshot. This record clarifies terminology and
precedence. It does not replace executable source. An archived record can
explain why a legacy fixture has a different answer, but it cannot make that
answer valid for a new request.

## Decision table

| item | current interpretation | source of behavior |
| --- | --- | --- |
scope,current decision boundary,release-control/decision.py
inputs,normalized request plus frozen snapshot,release-control/normalize.py
catalog,one published revision,release-control/catalog.py
identity,active member with required assurance,release-control/identities.py
time,issued request inside current window,release-control/windows.py
chain,all applicable required nodes,release-control/policy_chain.py
override,matching non-expired deny vetoes,release-control/overrides.py
quota,committed remaining capacity,release-control/quotas.py
audit,grant/deny conflict is rejected,release-control/audit.py
replay,history explains, never authorizes,release-control/replay.py
migration,legacy names are translated only,release-control/migrations.py
trace,order is retained for review,release-control/explain.py

## Review findings

1. A missing input fails closed before a live adapter is queried.
2. A record can be visible in history while being ineligible for a current decision.
3. A false applicable predicate is a denial; it is not equivalent to no predicate.
4. The current snapshot is authoritative for one decision and is never rebuilt halfway through it.
5. A helper name is not a contract: callers must check the actual aggregation and precedence.
6. Archived examples are evidence about an earlier revision, not exceptions to the current rule.
7. Current policy records intentionally keep declaration order for deterministic audit output.
8. The public result is boolean, but the review trace must retain every intermediate reason.
9. A successful early check cannot authorize a request whose later required check fails.
10. The final quota check is a read in this function; reservation is a separate operation.
11. Unknown channels, capabilities, and node kinds are not silently converted to stable defaults.
12. Normalization removes representational differences but never changes policy truth.

## Timeline fixtures

The following fixture labels are used by replay and operator review. They are
not independent specifications; each one is interpreted using the revision
and status rules above.

| id | recorded event | state | distinguishing fact | final stage |
| --- | --- | --- | --- | --- |
| 01 | 2025-10.1 | pass | active tenant and member | all checks |
| 02 | 2025-10.2 | deny | region mismatch | chain or veto |
| 03 | 2025-10.3 | replay-only | expired delegation | chain or veto |
| 04 | 2025-10.4 | missing | archived revision | all checks |
| 05 | 2025-10.5 | pass | active tenant and member | chain or veto |
| 06 | 2025-10.6 | deny | region mismatch | chain or veto |
| 07 | 2025-10.7 | replay-only | expired delegation | all checks |
| 08 | 2025-10.8 | missing | archived revision | chain or veto |
| 09 | 2025-10.9 | pass | active tenant and member | chain or veto |
| 10 | 2025-10.10 | deny | region mismatch | all checks |
| 11 | 2025-10.11 | replay-only | expired delegation | chain or veto |
| 12 | 2025-10.12 | missing | archived revision | chain or veto |
| 13 | 2025-10.13 | pass | active tenant and member | all checks |
| 14 | 2025-10.14 | deny | region mismatch | chain or veto |
| 15 | 2025-10.15 | replay-only | expired delegation | chain or veto |
| 16 | 2025-10.16 | missing | archived revision | all checks |
| 17 | 2025-10.17 | pass | active tenant and member | chain or veto |
| 18 | 2025-10.18 | deny | region mismatch | chain or veto |

## Questions settled by this record

- "Applicable" means that the current snapshot contains the named field and
  the node is part of the selected published chain.
- "Required" means a false result denies the request. An optional unknown node
  may be skipped only when the current node record marks it optional.
- An empty chain does not pass merely because no predicate returned false.
- A deny override is checked after ordinary eligibility but still vetoes the
  final grant.
- A replay observation can be retained for explanation without being consulted
  as a new authorization.
- The current policy revision is the one selected by the catalog, not the
  newest text file in this directory.
- Aliases affect parsing and migration only; they do not broaden capability.
- The words "any", "fallback", and "legacy" in old records must not be read as
  current aggregation instructions.

## Operator checklist

Before approving a review packet, verify normalization, catalog revision,
identity and assurance, time bounds, every chain result, deny precedence,
conflict detection, and quota. Then compare the trace with the recorded
revision. If a packet shows one passing node beside one failing required node,
the current decision is a denial even when the old replay result was a grant.

## Change note

The next revision must update this record, the current source, and the replay
fixtures together. A one-line helper change without a revision note is
incomplete. The review team specifically requests that readers distinguish
the intended all-required rule from any implementation that aggregates with
an any-of shortcut.

