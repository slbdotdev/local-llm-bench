# Internal note 0026: Failure Recovery

## Failure modes

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Operational notes

This note records a deliberately narrow decision about configuration review. The surrounding service may change, but the decision should remain easy to audit.

- Check the configuration review before changing the default behavior.
- Keep the owner and the review date next to the operational notes entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Inputs

This note records a deliberately narrow decision about configuration review. The surrounding service may change, but the decision should remain easy to audit.

- Check the configuration review before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Purpose

This note records a deliberately narrow decision about release notes. The surrounding service may change, but the decision should remain easy to audit.

- Check the release notes before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The written procedure is also a compact record of which assumptions were in force.

## Purpose

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The boundary is deliberately boring because predictable boundaries are easier to test.

## Purpose

This note records a deliberately narrow decision about data contracts. The surrounding service may change, but the decision should remain easy to audit.

- Check the data contracts before