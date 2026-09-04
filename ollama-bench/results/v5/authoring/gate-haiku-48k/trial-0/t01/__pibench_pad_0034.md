# Internal note 0034: Configuration Review

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
- Keep the owner and the review date next to the inputs entry.
- The review should distinguish a missing observation from an observation tha