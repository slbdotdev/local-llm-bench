# 2026-09: edge-case matrix

Status: CURRENT REVIEW FIXTURE.
Record identifier: rc-202609-edge-cases.

The matrix below is used to compare the source adapters. It is deliberately
larger than the small unit-test fixture because production failures often
occur where several individually ordinary facts meet. It does not grant an
exception to the current contract.

## Matrix

| id | tenant | identity | time | catalog | chain facts | veto/audit | result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | active | member+mfa | open | published | all true | none | true |
| E02 | active | member+mfa | open | published | region false | none | false |
| E03 | active | member+mfa | open | published | quota false | none | false |
| E04 | active | member+password | open | published | read true | none | false |
| E05 | active | absent | open | published | all true | none | false |
| E06 | active | member+mfa | expired | published | all true | none | false |
| E07 | active | member+mfa | open | missing | not selected | none | false |
| E08 | suspended | member+mfa | open | published | all true | none | false |
| E09 | active | member+mfa | open | published | one true, one false | none | false |
| E10 | active | member+mfa | open | published | all true | deny | false |
| E11 | active | member+mfa | open | published | all true | grant+deny conflict | false |
| E12 | active | delegated+mfa | open | published | delegation expired | none | false |
| E13 | active | member+webauthn | open | published | all true | none | true |
| E14 | active | member+mfa | before start | published | all true | none | false |
| E15 | active | member+mfa | open | retired | not selected | none | false |
| E16 | active | member+mfa | open | published | optional absent | none | true |
| E17 | active | member+mfa | open | published | required absent | none | false |
| E18 | active | member+mfa | open | published | all true | expired deny | true |
| E19 | active | member+mfa | open | published | all true | other tenant deny | true |
| E20 | active | member+mfa | open | published | all true | other capability deny | true |
| E21 | active | member+mfa | open | published | all true | archived deny | true |
| E22 | active | member+mfa | open | published | all true | replay-only grant | current rules |
| E23 | active | member+mfa | open | old revision | all true | none | false |
| E24 | active | member+mfa | open | published | false then true | none | false |

## Interpretation

Rows E02, E09, E12, and E24 are especially important. They distinguish
"all applicable required constraints" from an any-of shortcut. The fact that a
friendly node passes does not erase a failed required node. Rows E18-E21
distinguish current matching vetoes from historical or nonmatching records.
Rows E07, E15, and E23 distinguish a catalog miss or stale revision from a
published rule.

A reviewer must not infer behavior from the result column alone. The source
path, selected revision, and node applicability still have to be checked.
The matrix is a review aid and uses canonical names after normalization.

## Stability rules

- Comparisons use integer timestamps and a fixed 24-hour request age.
- Region and capability aliases are resolved before policy lookup.
- Current source wins over an archived fixture when replay and admission are
  compared.
- No default stable policy is selected for an unknown capability.
- No result is true merely because the chain contains at least one passing
  node.
- A deny and a conflict are both final vetoes.
- Quota availability is observed without mutation by the public function.
- The output of the public function is a boolean; explanations carry detail.

## Review sign-off

The edge-case suite is accepted only if the current call path agrees with the
matrix for every row. In particular, a case with one applicable true node and
one applicable false node is denied. This is the current invariant, not a
preference and not an interpretation left to the caller.

