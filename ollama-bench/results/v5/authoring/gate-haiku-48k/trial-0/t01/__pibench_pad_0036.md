# Internal note 0036: Failure Recovery

## Failure modes

This note records a deliberately narrow decision about service ownership. The surrounding service may change, but the decision should remain easy to audit.

- Check the service ownership before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

## Failure modes

This note records a deliberately narrow decision about cache invalidation. The surrounding service may change, but the decision should remain easy to audit.

- Check the cache invalidation before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Failure modes

This note records a deliberately narrow decision about audit records. The surrounding service may change, but the decision should remain easy to audit.

- Check the audit records before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- The written procedure is also a comp