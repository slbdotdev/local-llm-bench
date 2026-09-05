# 2026-09: source map for the release review

Status: CURRENT REVIEW INDEX.
Record identifier: rc-202609-source-map.

This index records the live dependency path for the public decision. It exists
because the function under review is intentionally small while its meaning is
distributed across adapters and historical migrations. A reviewer should trace
the request in this order and retain the same snapshot throughout.

## Live path

1. `normalize.py` rejects malformed requests and canonicalizes names.
2. `catalog.py` selects the published row whose revision matches the snapshot.
3. `identities.py` checks active membership and the capability's assurance.
4. `windows.py` checks not-before, expiry, and request age.
5. `policy_chain.py` evaluates the selected ordered nodes.
6. `overrides.py` applies a matching current deny.
7. `audit.py` rejects contradictory current observations.
8. `quotas.py` reads committed capacity as the final gate.

This is a serial path: a later stage cannot repair a failed earlier stage.
A helper with a name such as `all_required_pass` is useful evidence, but the
call site and the returned aggregation are the executable behavior.

## Current meanings

| phrase | meaning |
| --- | --- |
| current | selected by the published catalog revision |
| applicable | named by the selected chain and present in the frozen snapshot |
| required | false result denies the request |
| archived | available to replay and explanation, never new authorization |
| deny | a matching, unexpired veto |
| conflict | both grant and deny observations for one normalized request |
| reserve | a later side effect, not performed by the boolean decision |
| alias | parser spelling only; never a new capability |
| empty chain | invalid for grant and therefore false |

## Cross-check questions

- Does normalization happen before catalog lookup?
- Is a missing catalog row denied rather than replaced with stable?
- Does membership remain necessary when delegation exists?
- Does a failed region node remain applicable?
- Are old any-of examples confined to replay?
- Does a deny override remain a veto after all ordinary checks?
- Is quota read only after the chain and vetoes?
- Can an archived grant turn a current conflict into a pass?

The answers above are settled by the current source and the current contract
record. Older documents can explain why these questions were raised but cannot
change the answer.

## Review examples

| case | normalization | chain result | override | current result |
| --- | --- | --- | --- | --- |
| active read | pass | every node pass | none | grant |
| stale read | pass | window false | none | deny |
| active export | pass | region false | none | deny |
| active delegated write | pass | delegation false | none | deny |
| active read under incident | pass | every node pass | matching deny | deny |
| replayed old grant | pass | legacy result | archived only | current rules |
| contradictory audit | pass | every node pass | none | deny |
| exhausted quota | pass | every node pass | none | deny |

## Maintainer note

When changing aggregation or precedence, update the policy-chain implementation,
the public decision call path, the replay adapter, and the operator trace. A
single passing constraint is never sufficient evidence for a current grant when
another required constraint is applicable and false. This statement is the
review's central invariant.

