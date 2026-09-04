# Internal note 0007: Cache Invalidation

## Failure modes

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Failure modes

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Failure modes

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The boundary is deliberately boring beca