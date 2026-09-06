# Note: latency review, stages flagged

*Typed up from the latency review's whiteboard. It is about `window_s` and it is
about nothing else. It is kept because the review asked for it in writing, and it
has never been reconciled against the component documents it disagrees with.*

The stages whose documented window no longer matches what the review measured:

- `attestation`
- `schema`
- `watermark`

Windows were separated from release readiness three releases ago and this list is
not a readiness list; it is here so that the next latency review does not start
from nothing. Whoever picks it up should check each one against the module rather
than against this note, which is already a release out of date.
