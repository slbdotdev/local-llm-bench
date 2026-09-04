# Internal note 0036: Release Notes

## Inputs

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Open questions

This note records a deliberately narrow decision about retention windows. The surrounding service may change, but the decision should remain easy to audit.

- Check the retention windows before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Failure modes

This note records a deliberately narrow decision about data contracts. The surrounding service may change, but the decision should remain easy to audit.

- Check the data contracts before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertaint