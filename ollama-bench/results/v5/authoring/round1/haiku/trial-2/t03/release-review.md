NORTHSTAR EDGE RELAY — RELEASE REVIEW PACKET
Fictional change-control record for the 2034-06 relay release

Status and reading rules

This packet preserves the release review's pre-read, engineering discussion, approval
notes, and signed decision. The operations notebook is supporting material, not an
approval. A number can appear here as a proposal, test result, dashboard guide, or
policy value. The signed release decision at the end is authoritative for the ten
requested fields. “Mode” means the production forwarding behavior after rollout; it
does not mean the mode used by a shadow test.

System background

Northstar edge relays receive signed sensor packets over intermittent links. Admission
checks signatures and a maximum packet size, then places accepted packets in a bounded
queue. The forwarder sends packets to the archive and retries transient failures. Audit
events are stored separately from customer packets. The release review covers one
relay train and its production defaults; it does not revise the general archive or
vendor-management policies.

Pre-read: candidate settings

The pre-read proposed train `rly-2034.06`, with `rly-2029.11` retained as the rollback
image from an older deployment. A packaging note also called the candidate “June
train,” but the normalized train identifier is the value to use when the review
approves it.

For admission, the pre-read compared a 262144-byte ceiling with a 262208-byte ceiling.
The latter came from a lab test designed to exercise an oversized packet. One table
rendered 262144 bytes as 256 KiB; the binary display is only a convenience and does
not change the byte count.

The initial retry proposal allowed 5 attempts. The network team objected that repeated
retries could keep a dead link's queue occupied. A second proposal allowed 2 attempts
for very small sites. The review was asked to approve one ordinary production budget,
not to copy either proposal automatically.

A staging run used shadow mode on 2034-06-10 and reported clean signatures. Shadow
mode was selected for that run because the candidate could not yet own production
forwarding. The staging result is evidence about readiness, not the production rollout
date or the final mode.

The pre-read listed a rollback guide at “packet age over 20 minutes.” The dashboard
used a red line at 20 minutes and an amber line at 10 minutes. The reliability lead
said that packet age could be noisy, and asked for a trigger based on archive
acknowledgements instead. A separate 12-second archive request timeout appeared in a
trace and is not a rollback trigger.

The draft accountability table named the Edge Runtime group, with Priya Nandakumar
listed as the person expected to present the evidence. The group alias is useful for
notifications, but the review requires a named decision owner. A calendar draft placed
the review on 2034-06-13; it was marked tentative while the capacity test was pending.

The policy discussion compared a 15-minute verification window with a 30-minute
observation period. The longer period was suggested so that a slow site could be
watched through another link cycle. The shorter period was described as the actual
window for deciding whether the rollout gate had held. These are both durations, but
they are not interchangeable.

Audit storage discussion

The relay emits an audit event when it accepts a packet, when it exhausts its retry
budget, and when a batch is acknowledged by the archive. The audit store is queried by
the release team during verification. Customer packet retention is governed elsewhere.

Engineering proposed 60 days for relay audit events. The compliance worksheet showed
90 days for security logs, and the container image's local cleanup job showed 7 days.
The worksheet value applies to a broader security-log class; the cleanup value applies
only to ephemeral local copies. Neither should displace the relay audit policy.

Ticket and change references

Change control opened internal work item `NSR-418`. The release packet also contains a
vendor-contact template with the placeholder `EXT-771`, copied from an old example.
The procurement representative said that no external vendor ticket had been assigned
for this release. An internal work item is not an external ticket, and a placeholder
in a template is not evidence that a ticket exists.

Discussion and objections

The operations lead favored keeping the old 5-attempt retry setting because it reduced
visible packet loss during the last link outage. The safety reviewer replied that the
new queue limit made a smaller, fixed budget safer. The panel agreed to record the
retry budget as a count of attempts after the initial send, rather than as total
transmissions. This wording matters: a budget of 3 is not a budget of 3 retries plus
3 initial sends.

The capacity engineer measured a largest accepted packet of 262144 bytes in a clean
run. An oversized fixture at 262208 bytes was rejected as intended. The engineer's
report also mentioned a 256 KiB display label. The approved field is the maximum in
bytes, not the largest accidental fixture or the rounded display label.

The release manager asked whether production should begin in shadow mode and then
switch automatically. The panel rejected automatic switching. The release would be
approved for active forwarding only after the gate evidence was reviewed; shadow was
the pre-rollout test mode.

The reliability lead refined the rollback proposal. If the archive acknowledgement
gap exceeded two minutes, operators should stop the new forwarder and return to the
previous train. The lead explicitly said this should be written as an acknowledgement
gap, not as packet age and not as the 12-second request timeout. The panel requested
the comparison operator and units be retained in the signed wording.

The tentative calendar date was moved by one day to allow the capacity test and the
owner's evidence bundle to be reviewed. The final discussion used 2034-06-14 as the
rollout date. A post-rollout review was proposed for 2034-06-21, but that later date
is a follow-up appointment and not the rollout date.

Approval notes

The chair read back the proposed train, mode, byte limit, retry budget, date, trigger,
owner, verification window, audit lifetime, and ticket status. Participants corrected
the distinction between the internal change item and the absent external ticket. They
also corrected “three transmissions” to “three retries after the initial send.” The
chair recorded that a value in the read-back becomes controlling only when it appears
in the signed decision below.

The safety reviewer asked that the signed trigger preserve the phrase “archive
acknowledgement gap > 2 minutes.” The greater-than sign is part of the condition, not
a decorative separator. The chair agreed. The owner accepted responsibility for
collecting the gate evidence and for stopping the rollout if the trigger was met.

Signed release decision

Approved release train: `rly-2034.06`.

Approved production mode: `active-forward`. This means the new train is permitted to
own production forwarding after the gate passes; it is not the shadow mode used in
staging.

Approved maximum packet size: `262144 bytes`. The limit is an integer byte count. The
262208-byte fixture was rejected, and the 256 KiB label is not the field's spelling.

Approved retry budget: `3 retries after the initial send`. The requested integer is 3.

Approved rollout date: `2034-06-14`.

Approved rollback trigger: `archive acknowledgement gap > 2 minutes`.

Named decision owner: `Priya Nandakumar`.

The approved verification review window is `15 minutes`. It is the gate window used
immediately after the rollout decision, not the longer observation period proposed in
discussion.

Relay audit events will be retained for `60 days`. This is the relay audit policy and
does not change security-log retention or local-copy cleanup.

External ticket status: `not assigned`. The packet records no external vendor ticket
for this release. `NSR-418` remains the internal change-control work item, and `EXT-771`
is only a copied placeholder.

Signature block

Approved by the Northstar release panel on 2034-06-11. Decision owner: Priya
Nandakumar. The signature confirms the values in the signed release decision. Later
operational observations may be appended to the packet, but they do not amend the
approved values unless a new signed decision is issued.

Post-approval follow-up

The team will run the gate in a controlled region, check that rejected oversized
packets do not enter the queue, and verify that acknowledgement lag remains below the
rollback condition. The evidence bundle will be attached to internal work item
NSR-418. Procurement may open a vendor ticket in a future incident, but that possible
future action does not change the current status of no assigned external ticket.
