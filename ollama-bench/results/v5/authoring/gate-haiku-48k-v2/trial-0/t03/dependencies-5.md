# Internal note 0035: Batch Boundaries

## Inputs

This note records a deliberately narrow decision about batch boundaries. The surrounding service may change, but the decision should remain easy to audit.

- Check the batch boundaries before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Inputs

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Purpose

This note records a deliberately narrow decision about retention windows. The surrounding service may change, but the decision should remain easy to audit.

- Check the retention windows before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- Operators usually need the reason for a decision as well as the final state of 