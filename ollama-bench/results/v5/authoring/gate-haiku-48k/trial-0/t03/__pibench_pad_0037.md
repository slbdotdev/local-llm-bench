# Internal note 0037: Event Ordering

## Open questions

This note records a deliberately narrow decision about batch boundaries. The surrounding service may change, but the decision should remain easy to audit.

- Check the batch boundaries before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- The written procedure is also a compact record of which assumptions were in force.

## Open questions

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Failure modes

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- Operators usually need the reason for a decision as 