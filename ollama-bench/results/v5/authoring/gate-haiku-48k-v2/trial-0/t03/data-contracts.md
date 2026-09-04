# Internal note 0031: Data Contracts

## Purpose

This note records a deliberately narrow decision about batch boundaries. The surrounding service may change, but the decision should remain easy to audit.

- Check the batch boundaries before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Purpose

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- Operators usually need the reason for a decision as well as the final state of the record.

## Inputs

This note records a deliberately narrow decision about failure recovery. The surrounding service may change, but the decision should remain easy to audit.

- Check the failure recovery before changing the default behavior.
- Keep the owner and the review date next to the inputs entry.
- When the input is incomplete, preserve the uncertainty instead of manufactu