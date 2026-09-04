# Internal note 0033: Audit Records

## Inputs

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- The written procedure is also a compact record of which assumptions were in force.

## Operational notes

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Inputs

This note records a deliberately narrow decision about retention windows. The surrounding service may change, but the decision should remain easy to audit.

- Check the retention windows before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- When the input is incomplete, preserve the uncertainty instead of manufact