# Relay window contract

The relay platform decision owner is the ingestion group.  A decoder window begins at its
opening mark and ends immediately before its handoff mark: the right-hand boundary is
excluded.  This is the contract named by the visible decoder test.  The implementation's
public kind label is `half-open`; an older inclusive branch is not authoritative.

The rule is semantic rather than a request to change a test.  A caller that supplies an
empty window at equal marks receives an empty result, while a reversed or out-of-range
window remains invalid.
