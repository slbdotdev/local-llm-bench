# Internal note 0029: Queue Fairness

## Purpose

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Inputs

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Purpose

This note records a deliberately narrow decision about queue fairness. The surrounding service may change, but the decision should remain easy to audit.

- Check the queue fairness before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Open questions

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the open 