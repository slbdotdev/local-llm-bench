# Internal note 0034: Release Notes

## Purpose

This note records a deliberately narrow decision about data contracts. The surrounding service may change, but the decision should remain easy to audit.

- Check the data contracts before changing the default behavior.
- Keep the owner and the review date next to the purpose entry.
- The review should distinguish a missing observation from an observation that arrived late.

## Failure modes

This note records a deliberately narrow decision about event ordering. The surrounding service may change, but the decision should remain easy to audit.

- Check the event ordering before changing the default behavior.
- Keep the owner and the review date next to the failure modes entry.
- When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

## Open questions

This note records a deliberately narrow decision about release notes. The surrounding service may change, but the decision should remain easy to audit.

- Check the release notes before changing the default behavior.
- Keep the owner and the review date next to the open questions entry.
- Operators usually need the reason for a decision as well as the 