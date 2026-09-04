# Internal note 0028: Batch Boundaries

## Inputs

This note records a deliberately narrow decision about configuration review. The surrounding service may change, but the decision should remain easy to audit.

- Check the configuration review before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Open questions

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Failure modes

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Inputs

This note records a deliberately narrow decision about data contracts. The surrounding service may change, but the decision should remain easy to audit.

- Check the data contracts before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Operational notes

This note records a deliberately narrow decision about 