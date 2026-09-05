# Reliability standards

Module owner: Ivo Nordin
Team: sre
Review: quarterly game day
Cadence: 22 minutes



## Purpose

Reliability standards is maintained by Ivo Nordin for the sre group. It defines controls used during the quarterly game day and is reviewed every 22 minutes. The owner keeps the procedure actionable, while the service owner signs changes that affect production.

## Boundary

The operating boundary is the primary region. Requests outside it go to the platform duty manager. A handoff names the component, impact window, request key, and next observation time; a vague same-as-before handoff is rejected.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Start of work

At the start of an event, identify the component, write the incident key, and open the current on-call guide at //infra/handbook/oncall.md. That is a live entry point for today's operator and this occurrence is a current pointer that needs correction.

## State model

The workflow has four severity bands. A new event begins in observe, moves to contain only after evidence is recorded, and closes after a reviewer confirms recovery. Every transition names its actor and supporting artifact.

## Dependencies

Dependencies include the error-budget ledger, the primary region network path, the shared change calendar, and the owner rotation. A dependency failure is evidence to investigate, not permission to bypass approval or copy a command from history.

## Approval

The required control is a named owner and reviewer approval. The approver checks scope, rollback readiness, and customer impact. Evidence includes request ID, before and after state, actor, and exact UTC time.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Signals

The primary signal is customer-facing success rate. Secondary signals cover latency, saturation, and queue age. A missing signal is not a healthy signal; compare dashboards with the structured error-budget ledger record.

## Deployment

A deployment requires a ticket, artifact digest, rollback owner, and observation window. The promotion record is signed before production action. If the digest differs from the approved record, stop and return to the change owner.

## Recovery

Recovery starts by containing new work and preserving the first failing request. Select the smallest reversible action that tests the hypothesis. A rollback is complete only when both the customer signal and structured state recover.

## Data contract

Inputs carry a request key and UTC timestamp. Outputs name the component, result, owner, and evidence location. Missing fields are a failed handoff, not an invitation to guess. Redact secrets and customer payloads before sharing externally.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Review

The quarterly game day covers open incidents, overdue actions, recent changes, and exceptions. The chair records one owner per action. Closure requires evidence and a reviewer check; a green dashboard without a durable record is incomplete.

## Failure modes

Common failures are an unowned alert, stale digest, missing rollback, and handoff without evidence. Record detection, containment, correction, and prevention separately. The corrective action depends on whether the cause was demand, leak, dependency, or forecast.

## Maintenance

The owner checks links, examples, thresholds, and contact rotations during each review. Link checking includes the surrounding instruction, not just URL syntax. Remove an example only after checking training and incident dependencies.

## Access

Only the owner, reviewer, and approved delegates may edit this page. Read access is broad enough for responders. Audit entries record actor, reason, ticket, and affected section; a later correction appends rather than erases history.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Communication

During an active event, use the incident channel for coordination and the formal record for durable facts. Announcements name impact, state, owner, and next update. After closure, publish outcome and link the evidence bundle.

## Exceptions

An exception needs scope, expiry, approving owner, and compensating control. Permanent exceptions are rejected. If an exception affects relocation, consult the migration register and the current guide owner; do not revive an archived destination.

## Capacity

Capacity review uses peak traffic, queued work, and recovery time. Shed optional work before critical work. Capacity changes follow the same approval and evidence path as deployments, with a named rollback owner.

## Decision record

The current decision is to use the relocated runbook as the destination for new operational links while preserving historical references. This distinction means live pointers are corrected and records of past state remain intact.

Before closing this module, verify the current pointer at //infra/handbook/oncall.md and record the result in the audit.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Closing

Close only when the requested control is implemented, evidence is linked, the owner acknowledges it, and the next review date is set. The final check searches the exact old path and reviews each result in context.

## Near miss

A suffix is a different path: //infra/handbook/oncall.md/appendix. Do not count it in the audit. The literal old path can be prose, a live pointer, or evidence; heading, date, and sentence role determine the action.

## Vocabulary

Current means an operator is expected to use the instruction now. Historical means the text reports what happened or was true at an earlier time. Evidence supports a decision. Pointer directs a reader.

## Cross-module handoff

The sre group publishes owner, escalation, and rollback metadata before the quarterly game day. Shared vocabulary does not make thresholds interchangeable: use this module's evidence requirements and approval boundary.

| Check | Owner | Evidence | Cadence |
|---|---|---|---|
| intake | Ivo Nordin | request key | each event |
| containment | sre | state transition | each event |
| recovery | duty lead | signal comparison | 22 minutes |
| closure | reviewer | signed record | monthly |

## Audit sample

Each review samples one successful and one failed event. Compare the request log, error-budget ledger, decision record, and communication timeline. Disagreement keeps the item open until an owner reconciles the sources.

## Operator checklist

Before action: identify scope, verify owner, check change freeze, and read the current guide. During action: record command, result, and timestamp. After action: compare signals, attach evidence, and schedule review.

## Current index entry

The active escalation link in the shared index is [on-call guide](//infra/handbook/oncall.md). Use the relocated destination for all new links.
