# Internal note 0025: Batch Boundaries

## Inputs

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Failure modes

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Failure modes

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Inputs

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Failure modes

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The written procedure is also a compact record of which assumptions were in force.

## Purpose

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Open questions

This note records a deliberately narrow decision about service ownership. The surrounding service may change