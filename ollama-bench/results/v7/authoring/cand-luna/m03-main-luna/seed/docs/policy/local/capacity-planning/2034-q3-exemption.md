# LP-07 — capacity-exception exemptions, this quarter

- Status: **in force**
- Supersedes: LP-05 (exempted by owner name; retired)
- Scope: the quarterly capacity-exception report only. It grants nothing outside
  that report and nothing to any other document under `docs/policy/`.

## The ruling

A capacity exception is exempt from the quarterly report when, and only when,
`data/capacity-audit-log.csv` records a `disposition` of `tracked-elsewhere` for its
stage. Every other disposition value — including `open` and `no-exception` — carries
no exemption. The `reviewed_on` and `reviewer` columns are kept for the audit trail
only; they do not affect scope, and a stage is never exempted or included on the
strength of a date alone.

## Why this is not a general policy

The pages under `docs/policy/` that are not under `local/` are general and predate
the audit log; none of them mentions a capacity exception because none of them was
written with one in mind. Filing this ruling under `local/` rather than editing one
of them keeps a subject-specific ruling from being read as though it applied more
broadly than it does.

## History

LP-05 exempted a stage by the name of its owning team, which stopped working the first
quarter a stage changed owners mid-cycle. This ruling reads the audit log instead,
which is dated per stage and does not move when a person does.

## Standing

This ruling is scoped to the capacity-exception report and stays in force until a
later ruling on the same subject supersedes it in writing. Nothing else in this
repository revokes it, and nothing compiled before it existed may be read as though
it had already applied.
