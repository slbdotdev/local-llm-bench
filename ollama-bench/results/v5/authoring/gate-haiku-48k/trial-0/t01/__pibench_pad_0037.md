# Internal note 0037: Queue Fairness

## Failure modes

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Failure modes

This note records a deliberately narrow decision about release notes. The surrounding service may change, but the decision should remain easy to audit.

- Check the release notes before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Failure modes

This note records a deliberately narrow decision about schema migration. The surrounding service may change, but the decision should remain easy to audit.

- Check the schema migration before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The review should distinguish a missing obs