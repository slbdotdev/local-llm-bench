# Internal note 0038: Batch Boundaries

## Failure modes

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Purpose

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Open questions

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- The written procedure is also a compact rec