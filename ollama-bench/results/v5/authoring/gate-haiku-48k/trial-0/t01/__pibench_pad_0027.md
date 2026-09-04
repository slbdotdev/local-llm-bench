# Internal note 0027: Cache Invalidation

## Operational notes

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Operational notes

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Failure modes

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Open questions

This note records a deliberately narrow decision about queue fairness. The surrounding service may change, but the decision should remain easy to audit.

- Check the queue fairness before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Failure modes

This note records a deliberately narrow decision about queue fairness. The surrounding service may change, but the decision should remain easy to audit.

- Check the queue fairness before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Inputs

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Operational notes

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before c