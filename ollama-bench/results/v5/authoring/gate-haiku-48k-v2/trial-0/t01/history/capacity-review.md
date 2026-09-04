# Internal note 0027: Cache Invalidation

## Inputs

This note records a deliberately narrow decision about release notes. The surrounding service may change, but the decision should remain easy to audit.

- Check the release notes before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Operational notes

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Purpose

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Operational notes

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Purpose

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Inputs

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Inputs

This note records a deliberately narrow decision about retention windows. The surrounding service may change, but the decision should remain easy to audit.

- Check the retention windows before changing the default behavior.
-