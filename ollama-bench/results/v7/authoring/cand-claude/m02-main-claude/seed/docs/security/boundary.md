# Security boundary - configuration-surface freezes

*Numbered clauses, newest last. A clause freezes a team's stages against one
named class of change; it never freezes a stage by name, because stages move
between teams and a name-based freeze has gone stale before, silently.*

## SEC-CFG-2 (superseded)

Froze every stage on-call to Client Integrations against a limit increase,
after a capacity incident traced to an ungated increase. Superseded once the
manifest gained a startup check for exactly that case (see `docs/operations.md`
restart procedure); the freeze no longer does any work the manifest doesn't.

## SEC-CFG-3 (withdrawn)

Proposed freezing every stage above a limit of 500 records against any
configuration-surface change at all, on the theory that a large stage is a
risky one to touch. Withdrawn: size and risk turned out to be uncorrelated in
the incident log, and the clause would have frozen stages that had never had
an incident.

## SEC-CFG-4 (**in force**)

A stage on-call to the **Delivery Engineering** team - see that stage's component document, where
the per-stage ownership statement is authoritative - is
frozen against any rename of a key in its published configuration
surface, including this one, until that team signs off in writing. The team's
sign-off is not requested by filing the rename; it is a separate, later step
and out of scope for whoever carries out ISSUE-214.

A stage this clause freezes belongs in the report's second field, never in the
first and never silently omitted: the report exists so the frozen team can see
what it blocked.

## What this boundary does not cover

It says nothing about a stage that is not published under the current API
contract; an unpublished stage was never in scope for ISSUE-214 regardless of
which team owns it, and this boundary has no opinion on it.
