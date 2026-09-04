NORTHSTAR EDGE RELAY — OPERATIONS NOTEBOOK
Working material for a fictional rollout review

This notebook collects observations made while testing the Northstar edge relay, a
small service that accepts signed packets from remote sensors and forwards them to the
central archive. It is not itself an approval record. Numbers in this notebook may be
measurements, defaults, proposals, or values copied from an older deployment.

The relay has three stages: admission checks the signature and packet shape, a bounded
local queue holds accepted packets, and forwarding sends batches to the archive. A
packet can be accepted locally and still need retrying later. Therefore an accepted
packet count is not the same thing as a successfully archived packet count.

During a laboratory run, the largest packet observed was 262208 bytes. The test
fixture was intentionally a few bytes above the normal configured ceiling so that the
admission error path could be checked. The run report also lists a 262144-byte sample
because that was the largest packet accepted by the older relay image. Neither number
alone establishes the approved production limit.

The relay retried a disconnected archive connection five times in one stress test.
That was a test harness setting chosen to make failures reproducible. A separate
operator note suggests four attempts for remote sites with expensive links. Retry
counts in this notebook are not a release decision.

The staging team ran the candidate image in shadow mode on 2034-06-10. Shadow mode
sent copies to a test archive without allowing the candidate to own production
forwarding. A dashboard export labels 2034-06-12 as the date on which the first
production-like traffic was observed; that label refers to a measurement window, not a
rollout commitment.

The packet-age graph has a red guide at 20 minutes and an amber guide at 10 minutes.
Those are dashboard guides. In a later incident simulation, an operator saw a packet
remain queued for 18 minutes before the archive recovered. The observation is useful
for sizing the queue but does not define the rollback condition.

The reliability team proposed retaining relay audit events for 30 days. The compliance
worksheet uses 90 days for a different class of security logs, and the development
container deletes its local audit copy after 7 days. These lifetimes belong to
different stores and should not be substituted for an approved policy.

The change-control system issued internal work item NSR-418. A copied chat message
refers to EXT-771 as a possible vendor ticket, but no vendor contact had been opened at
the time of the notebook update. The internal work item and a possible external ticket
are separate concepts.

Additional observations

One old relay image reports train `rly-2029.11`, while the candidate package was built
from train `rly-2034.06`. A release engineer wrote “mode=shadow first” in a scratchpad,
which described the safe test sequence rather than the eventual production mode.

The queue's configured byte ceiling was printed in binary units by the diagnostic
tool. A storage dashboard rounded the same region's capacity to 256 KiB. The dashboard
rounding is presentation only; do not silently replace an integer byte limit with a
human-readable approximation.

An archive timeout of 12 seconds appeared in one trace. It is the network timeout for
one request, not a review window and not a rollback trigger. Another trace recorded a
9-minute drain after a canary was stopped. Both durations are operational facts, but
neither is an approved field without the signed decision.

The notebook was attached to the review packet so that the panel could see why several
candidate values were rejected. Its attachment to that packet does not grant it the
authority of the signed release decision.
